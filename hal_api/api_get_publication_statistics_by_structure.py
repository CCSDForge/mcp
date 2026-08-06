import aiohttp

BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_publication_stats(
    struct_id: int,
    start_year: int,
    end_year: int,
    rows: int = 10000,
) -> dict:
    """
    Interroge l'API de recherche HAL pour récupérer les publications d'une
    structure sur une période donnée (année de production + type de document).

    Returns:
        dict avec:
            - num_found (int): nombre total de publications correspondantes
            - total_returned (int): nombre réellement récupéré (<= rows)
            - has_more (bool): True si num_found > total_returned (troncature)
            - publications (list[dict]): [{"year": ..., "type": ...}, ...]
            - query_url (str)
        ou en cas d'erreur:
            - error (str)
            - query_url (str)
    """
    params = {
        "q": "*:*",
        "fq": [
            f"structId_i:{struct_id}",
            f"producedDateY_i:[{start_year} TO {end_year}]",
        ],
        "fl": "producedDateY_i,docType_s",
        "rows": rows,
        "wt": "json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as resp:
            query_url = str(resp.url)

            if resp.status != 200:
                return {
                    "error": f"L'API HAL a répondu avec le code {resp.status}",
                    "query_url": query_url,
                }

            data = await resp.json()
            response_block = data.get("response", {})
            docs = response_block.get("docs", [])
            num_found = response_block.get("numFound", len(docs))

            publications = [
                {
                    "year": d.get("producedDateY_i"),
                    "type": d.get("docType_s"),
                }
                for d in docs
            ]

            return {
                "num_found": num_found,
                "total_returned": len(publications),
                "has_more": num_found > len(publications),
                "publications": publications,
                "query_url": query_url,
            }