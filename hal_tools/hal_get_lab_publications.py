from core.mcp import mcp
from hal_api import search_lab_publications


@mcp.tool()
async def hal_get_lab_publications(structure_id: str, year: int) -> dict:
    """
    Analyse les mots-clés des publications HAL d'une structure pour une année.
    """

    result = await search_lab_publications(structure_id, year)

    if "error" in result:
        return result

    return {
        "raw_text_report": result["raw_text_report"],
        "num_found": result["num_found"],
    }