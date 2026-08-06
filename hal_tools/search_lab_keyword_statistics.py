from core.mcp import mcp
from hal_api.api_search_lab_keyword_statistics import search_lab_keywords


@mcp.tool()
async def search_lab_keyword_statistics(
    structure_id: str,
    year: int
) -> dict:
    """
    Analyse les thématiques de recherche d'une structure HAL.

    IMPORTANT :
    - Ce tool ne retourne PAS les publications.
    - Solr réalise directement l'agrégation des mots-clés.
    - Le champ keyword_aggregation contient déjà les fréquences calculées.
    - Le LLM ne doit effectuer aucun comptage.

    Workflow :
    1. Si l'utilisateur donne un nom de structure,
       utiliser d'abord search_structure pour obtenir structure_id.
    2. Utiliser ce tool avec l'identifiant HAL et l'année.

    Résultat :
    - total_publications : nombre total de publications trouvées
    - keyword_aggregation : mots-clés avec leur nombre d'occurrences
    """


    result = await search_lab_keywords(
        structure_id,
        year
    )


    return result