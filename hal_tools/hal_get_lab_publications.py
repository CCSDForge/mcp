from core.mcp import mcp
from hal_api import search_lab_keywords


@mcp.tool()
async def hal_get_lab_publications(
    structure_id: str,
    start_date: str,
    end_date: str
) -> dict:
    """
    Analyse les thèmes de recherche d'une structure HAL.

    Les dates doivent être au format YYYY-MM-DD.

    Exemple :
    start_date="2025-01-01"
    end_date="2025-12-31"

    IMPORTANT :
    - L'API Solr réalise directement l'agrégation des mots-clés.
    - Aucun document individuel n'est envoyé au LLM.
    - keyword_aggregation contient déjà les comptages calculés.

    Si l'utilisateur donne uniquement le nom d'une structure,
    utiliser d'abord search_structure pour obtenir structure_id.
    """

    return await search_lab_keywords(
        structure_id,
        start_date,
        end_date
    )