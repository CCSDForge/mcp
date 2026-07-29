import aiohttp
from collections import Counter

BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_lab_publications(structure_id: str, year: int, rows: int = 1000) -> dict:
    """
    Récupère et compte les mots-clés des publications HAL d'une structure,
    pour une année donnée. Pagine sur tous les résultats.

    Returns:
        dict avec:
            - structure (str)
            - year (int)
            - num_found (int)
            - keywords (dict[str, int]): mot-clé -> nombre d'occurrences,
              trié par fréquence décroissante
            - pagination_log (list[str]): messages de progression
    """
    counter = Counter()
    start = 0
    total = None
    pagination_log = []

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        while True:
            params = {
                "q": "*:*",
                "fq": [
                    f"structId_i:{structure_id}",
                    f"producedDateY_i:{year}",
                ],
                "fl": "keyword_s",
                "rows": rows,
                "start": start,
                "wt": "json",
                "sort": "docid asc",
            }
            async with session.get(BASE_URL, params=params) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return {"error": f"Erreur {resp.status}: {text}"}
                data = await resp.json()

            response = data["response"]
            if total is None:
                total = response["numFound"]
                pagination_log.append(f"Publications trouvées : {total}")

            docs = response["docs"]
            if not docs:
                break

            for doc in docs:
                keywords = doc.get("keyword_s", [])
                if isinstance(keywords, str):
                    keywords = [keywords]
                for kw in keywords:
                    kw = kw.strip().lower()
                    if kw:
                        counter[kw] += 1

            start += len(docs)
            pagination_log.append(f"{start}/{total} publications traitées")
            if start >= total:
                break

    return {
        "structure": structure_id,
        "year": year,
        "num_found": total or 0,
        "keywords": dict(counter.most_common()),
        "pagination_log": pagination_log,
    }