from core.mcp import mcp
from hal_api import search_lab_publications


def _format_report(pagination_log: list[str], keywords: dict, top_n: int = 30) -> str:
    lines = list(pagination_log)
    lines.append("")
    lines.append(f"Top {top_n} mots-clés :")
    top_items = list(keywords.items())[:top_n]
    for kw, count in top_items:
        lines.append(f"{kw} : {count}")
    return "\n".join(lines)


@mcp.tool()
async def hal_get_lab_publications(structure_id: str, year: int) -> dict:
    """
    Compte les mots-clés des publications HAL d'une structure pour une année donnée.

    PRÉREQUIS : structure_id doit être un identifiant HAL NUMÉRIQUE déjà connu
    (structId_i). Si tu n'as qu'un nom de structure, résous-le d'abord avec le
    tool de recherche de structure.

    Args:
        structure_id: identifiant HAL numérique de la structure.
        year: année exacte (ex: 2025).

    Returns:
        raw_text_report (str): rapport texte déjà formaté (progression +
            top 30 mots-clés avec comptage exact). C'est la SEULE source
            à utiliser pour répondre à l'utilisateur.
        num_found (int)

    RÈGLE STRICTE : recopie "raw_text_report" tel quel dans un bloc de code,
    sans reformuler, sans recalculer, sans en omettre ni en inventer.
    """
    result = await search_lab_publications(structure_id=structure_id, year=year)

    if "error" in result:
        return {"error": result["error"]}

    raw_text_report = _format_report(result["pagination_log"], result["keywords"])

    return {
        "raw_text_report": raw_text_report,
        "num_found": result["num_found"],
    }