from core.mcp import mcp
from hal_api import search_lab_publications
from utils import format_keyword_report


@mcp.tool()
async def hal_get_lab_publications(structure_id: str, year: int) -> dict:
    """
    Analyse THÉMATIQUE des publications HAL d'un laboratoire/structure :
    compte la fréquence des MOTS-CLÉS (keyword_s) pour identifier les sujets
    de recherche dominants ou émergents d'une structure pour une année donnée.

    À UTILISER QUAND la question porte sur : "thématiques", "sujets de
    recherche", "mots-clés", "domaines émergents", "de quoi parlent les
    publications", "tendances de recherche".

    NE PAS CONFONDRE avec un tool de statistiques/comptage de publications
    (nombre de publications, par type de document, par année, etc.) : ce
    tool-ci ne renvoie AUCUN chiffre de volume de publications au-delà du
    total trouvé — il sert uniquement à analyser le CONTENU thématique via
    les mots-clés.

    PRÉREQUIS : structure_id doit être un identifiant HAL NUMÉRIQUE déjà
    connu (structId_i). Si tu n'as qu'un nom de structure (ex: "Université
    Claude Bernard Lyon 1"), résous-le D'ABORD avec le tool de recherche de
    structure.

    Args:
        structure_id: identifiant HAL numérique de la structure.
        year: année exacte (ex: 2025).

    Returns:
        raw_text_report (str): rapport texte déjà formaté (progression +
            top 30 mots-clés avec comptage exact). SEULE source à utiliser
            pour répondre à l'utilisateur.
        num_found (int)

    RÈGLE STRICTE : recopie "raw_text_report" tel quel dans un bloc de code,
    sans reformuler, sans recalculer, sans en omettre ni en inventer.
    """
    result = await search_lab_publications(structure_id=structure_id, year=year)

    if "error" in result:
        return {"error": result["error"]}

    raw_text_report = format_keyword_report(result["pagination_log"], result["keywords"])

    return {
        "raw_text_report": raw_text_report,
        "num_found": result["num_found"],
    }