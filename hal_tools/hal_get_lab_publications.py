from core.mcp import mcp
from hal_api import search_lab_publications


@mcp.tool()
async def hal_get_lab_publications(structure_id: str, year: int) -> dict:
    """
Analyse les mots-clés des publications HAL.

IMPORTANT

Ce tool analyse TOUJOURS l'intégralité des publications
renvoyées par l'API HAL.

Il n'utilise jamais un échantillon.

La fonction interne parcourt automatiquement toutes les pages
de résultats jusqu'à ce que les `numFound` publications aient
été traitées.

Le nombre de publications effectivement analysées est renvoyé
dans `num_found`.

Si l'utilisateur fournit un nom de structure et non un
identifiant HAL, il faut d'abord appeler `search_structure`
pour obtenir le `structure_id`.
"""

    result = await search_lab_publications(structure_id, year)

    if "error" in result:
        return result

    return {
        "raw_text_report": result["raw_text_report"],
        "num_found": result["num_found"],
    }