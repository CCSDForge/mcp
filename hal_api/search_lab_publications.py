import aiohttp
from datetime import datetime


BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_lab_publications(
    structure_id: str,
    start_date: str,
    end_date: str,
    limit: int = 30
) -> dict:
    """
    Agrégation Solr des mots-clés HAL sur une période donnée.

    start_date et end_date au format YYYY-MM-DD.

    Exemple :
    start_date="2025-01-01"
    end_date="2025-12-31"
    """

    # Vérification format date
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")


    params = {
        "q": "*:*",

        "fq": [
            f"structId_i:{structure_id}",
            f"producedDate_tdate:[{start_date}T00:00:00Z TO {end_date}T23:59:59Z]"
        ],

        # Agrégation Solr
        "facet": "true",
        "facet.field": "keyword_s",
        "facet.limit": limit,
        "facet.sort": "count",

        # aucun document
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
                    "error": await resp.text()
                }

            data = await resp.json()


    facet_values = (
        data
        .get("facet_counts", {})
        .get("facet_fields", {})
        .get("keyword_s", [])
    )


    keywords = {}

    for i in range(0, len(facet_values), 2):
        keywords[facet_values[i]] = facet_values[i + 1]


    return {
        "structure_id": structure_id,
        "start_date": start_date,
        "end_date": end_date,
        "num_found": data["response"]["numFound"],
        "keyword_aggregation": keywords
    }