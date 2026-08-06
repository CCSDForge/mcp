from core.mcp import mcp
from hal_api.api_search_authors import search_authors


@mcp.tool()
async def search_authors(query: str, rows: int = 10):
    """
    Search authors in the HAL referential (/ref/author) by name or name fragment.

    USE THIS TOOL to resolve an author name to their HAL id(s). This tool returns identity information only
    (name, HAL id, validation status).

    DO NOT use this tool to find an author's affiliations, lab, or career
    history — use get_author_affiliations for that instead.
    DO NOT use this tool to find an author's publications — use a
    publication-search tool for that instead.

    Args:
        query: author name or fragment to search for (e.g. "Yutong Fei")
        rows: maximum number of results (default: 10)

    Returns:
        num_found: total number of matching authors in HAL
        total_returned: number of authors actually returned
        has_more: True if num_found > total_returned (results truncated)
        authors: list of {name, hal_id, docid, statut_validation}
                 (these are the ONLY field names that exist — do not invent
                 others such as "id_hal" or "nom_complet")
        query_url: exact URL called (for traceability)

    ANTI-HALLUCINATION RULE: only report name/hal_id/status values explicitly
    present in "authors" below. If num_found is 0, say so explicitly — do not
    guess an author's identity or details, and do not silently pick one
    homonym if several are returned.
    """
    if not query or not query.strip():
        return {"error": "Le paramètre 'query' est requis et ne peut pas être vide"}

    result = await search_authors(query.strip(), rows=rows)
    if "error" in result:
        return {"error": result["error"], "query_url": result.get("query_url")}
    return result