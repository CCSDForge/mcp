import aiohttp
from collections import Counter

BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_lab_publications(
    structure_id: str,
    year: int,
    rows: int = 1000
) -> dict:
    """
    Récupère toutes les publications HAL d'une structure pour une année
    donnée et calcule la fréquence des mots-clés.

    La pagination permet de parcourir tous les résultats HAL.
    Le LLM ne reçoit jamais les publications individuelles,
    uniquement les statistiques agrégées.
    """

    counter = Counter()
    start = 0
    total = None

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=60)
    ) as session:

        while True:

            params = {
                "q": "*:*",
                "fq": [
                    f"structId_i:{structure_id}",
                    f"producedDateY_i:{year}"
                ],
                "fl": "keyword_s",
                "rows": rows,
                "start": start,
                "wt": "json",
                "sort": "docid asc"
            }

            async with session.get(BASE_URL, params=params) as resp:

                if resp.status != 200:
                    return {
                        "error": f"Erreur HAL {resp.status}: {await resp.text()}"
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


            # Toutes les publications ont été traitées
            if start >= total:
                break


    return {
        "structure_id": structure_id,
        "year": year,
        "num_found": total or 0,
        "total_keywords": len(counter),

        "top_keywords": [
            {
                "keyword": kw,
                "count": count
            }
            for kw, count in counter.most_common(30)
        ]
    }