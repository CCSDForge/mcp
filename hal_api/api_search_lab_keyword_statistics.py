import aiohttp


BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_lab_keywords(
    structure_id: str,
    year: int,
    limit: int = 30
) -> dict:
    """
    Recherche les mots-clés agrégés d'une structure HAL.

    Solr effectue directement le comptage via les facettes.
    on cherche pas la liste de publications ...
    """

    params = {
        "q": "*:*",
        "fq": [
            f"structId_i:{structure_id}",
            f"producedDateY_i:{year}"
        ],

        # Agrégation Solr
        "facet": "true",
        "facet.field": "keyword_s",
        "facet.limit": limit,
        "facet.sort": "count",

        # Ne retourne aucune publication
        "rows": 0,

        "wt": "json"
    }


    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=60)
    ) as session:

        async with session.get(
            BASE_URL,
            params=params
        ) as resp:

            if resp.status != 200:
                return {
                    "error": f"Erreur HAL {resp.status}: {await resp.text()}"
                }


            data = await resp.json()


    # Nombre total de publications
    total_publications = data["response"]["numFound"]


    # Solr retourne :
    # [
    #   "mot1", 120,
    #   "mot2", 90
    # ]

    facet_values = (
        data
        .get("facet_counts", {})
        .get("facet_fields", {})
        .get("keyword_s", [])
    )


    keyword_aggregation = {}

    for i in range(0, len(facet_values), 2):
        keyword_aggregation[facet_values[i]] = facet_values[i + 1]


    return {
        "structure_id": structure_id,
        "year": year,
        "total_publications": total_publications,
        "keyword_aggregation": keyword_aggregation
    }