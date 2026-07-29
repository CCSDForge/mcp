from core.mcp import mcp
from hal_api import search_lab_publications


@mcp.tool()
async def hal_get_lab_publications(
    structure_id: str,
    year: int
) -> dict:
    """
    Analyse les thématiques de recherche d'une structure HAL.

    IMPORTANT :
    - Ce tool analyse toutes les publications HAL correspondant
      aux critères.
    - Il ne travaille jamais sur un échantillon.
    - La pagination HAL est automatique jusqu'au dernier document.
    - Le résultat retourné est une agrégation des mots-clés,
      pas la liste des publications.

    WORKFLOW :
    1. Si l'utilisateur donne un nom de laboratoire ou structure,
       utiliser d'abord search_structure pour obtenir structure_id.
    2. Utiliser ensuite ce tool avec l'identifiant HAL numérique.

    Retour :
    - num_found : nombre total de publications analysées
    - top_keywords : 30 mots-clés les plus fréquents
    """

    result = await search_lab_publications(
        structure_id=structure_id,
        year=year
    )


    if "error" in result:
        return result


    return result