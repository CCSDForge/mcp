import aiohttp
from collections import Counter

BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_lab_publications(structure_id: str, year: int | None = None, rows: int = 1000) -> dict:
    """
    Reproduit exactement la logique du script de référence : pagine sur
    toutes les publications d'une structure (et, si fourni, une année
    précise), compte les mots-clés (normalisés en minuscules), et journalise
    la progression de récupération.

    Args:
        structure_id: identifiant HAL numérique de la structure (structId_i).
        year: année exacte à filtrer (producedDateY_i:{year}), ou None pour
            toutes les années.
        rows: taille de page pour la pagination (défaut: 1000, comme le script).

    Returns:
        dict avec:
            - num_found (int): nombre total de publications trouvées
            - total_returned (int): nombre de publications effectivement parcourues
            - counter (dict[str, int]): mot-clé (minuscule) -> nombre de publications
            - pagination_log (list[str]): lignes "X/Y publications récupérées"
            - query_url (str)
        ou {"error": ..., "query_url": ...} en cas d'échec.
    """
    fq = [f"structId_i:{structure_id}"]
    if year is not None:
        fq.append(f"producedDateY_i:{year}")

    counter = Counter()
    pagination_log = []
    start = 0
    total = None
    query_url = None

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        while True:
            params = {
                "q": "*:*",
                "fq": fq,
                "fl": "keyword_s",
                "wt": "json",
                "rows": rows,
                "start": start,
            }
            async with session.get(BASE_URL, params=params) as resp:
                query_url = str(resp.url)
                if resp.status != 200:
                    text = await resp.text()
                    return {
                        "error": f"Erreur {resp.status}\n{text}",
                        "query_url": query_url,
                    }
                data = await resp.json()

            response = data["response"]
            if total is None:
                total = response["numFound"]
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
            pagination_log.append(f"{start}/{total} publications récupérées")
            if start >= total:
                break

    return {
        "num_found": total or 0,
        "total_returned": start,
        "counter": dict(counter),
        "pagination_log": pagination_log,
        "query_url": query_url,
    }