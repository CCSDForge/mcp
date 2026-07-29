from core.mcp import mcp
from hal_api.search_publication_anr_open_access import search_publication_anr_open_access
from utils import aggregate_publications_by_year_and_doctype

MAX_ROWS = 1000


def _build_period_applied(start_year, end_year):
    return (
        f"{start_year or '...'} à {end_year or '...'}"
        if (start_year or end_year)
        else "aucune restriction (toutes années confondues)"
    )


@mcp.tool()
async def count_anr_publications(
    open_access: bool | None = None,
    struct_id: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
):

    if start_year is not None and end_year is not None and start_year > end_year:
        raise ValueError(f"start_year ({start_year}) must be <= end_year ({end_year})")

    try:
        result = await search_publication_anr_open_access(
            open_access=open_access,
            struct_id=struct_id,
            start_year=start_year,
            end_year=end_year,
            rows=0,
        )
    except Exception as e:
        return {"error": f"Erreur inattendue lors de l'appel à HAL : {e}"}

    if "error" in result:
        return {"error": result["error"], "query_url": result.get("query_url")}

    return {
        "total_matching_hal": result["num_found"],
        "open_access_filter": open_access,
        "struct_id": struct_id,
        "period_applied": _build_period_applied(start_year, end_year),
        "query_url": result["query_url"],
    }
@mcp.tool()
async def get_anr_publications(
    open_access: bool | None = None,
    struct_id: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    rows: int = 100,
):
    """
    Search and list HAL publications funded by ANR, with optional filters.

    Use this tool ONLY when the user asks for a list, examples, or details of
    specific publications. If the user only asks "how many" / "combien de"
    publications, use count_anr_publications instead — do not use this tool
    for count-only questions.

    Parameters:
        open_access: filter on open access status (True/False/None = no filter, all statuses)
        struct_id: HAL structure id to restrict to one institution (e.g. 116256)
        start_year: only set if explicitly requested by the user; leave None otherwise.
        end_year: only set if explicitly requested by the user; leave None otherwise.
        rows: maximum number of publications actually retrieved and detailed
            (default: 100, max: 1000). This does NOT limit the true total count
            reported in "total_matching_hal".
    """
    if start_year is not None and end_year is not None and start_year > end_year:
        raise ValueError(f"start_year ({start_year}) must be <= end_year ({end_year})")

    rows = max(1, min(rows, MAX_ROWS))

    try:
        result = await search_publication_anr_open_access(
            open_access=open_access,
            struct_id=struct_id,
            start_year=start_year,
            end_year=end_year,
            rows=rows,
        )
    except Exception as e:
        return {"error": f"Erreur inattendue lors de l'appel à HAL : {e}"}

    if "error" in result:
        return {"error": result["error"], "query_url": result.get("query_url")}

    publications = result["publications"]
    stats = aggregate_publications_by_year_and_doctype(publications)

    return {
        "total_matching_hal": result["num_found"],
        "total_returned": len(publications),
        "open_access_filter": open_access,
        "struct_id": struct_id,
        "period_applied": _build_period_applied(start_year, end_year),
        "stats_by_year_and_type": stats,
        "publications": publications,
        "query_url": result["query_url"],
    }