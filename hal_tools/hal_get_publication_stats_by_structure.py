from core.mcp import mcp
from hal_api.search_publication_stats import search_publication_stats


@mcp.tool()
async def hal_get_publication_stats_by_structure(
    struct_id: int,
    start_year: int,
    end_year: int,
):
    """
    Get the number of HAL publications for a given structure and period,
    broken down by year and document type.

    Parameters:
        struct_id: HAL structure id (e.g. 194495 for Université Claude Bernard Lyon 1)
        start_year: first year of the period (inclusive)
        end_year: last year of the period (inclusive), must be >= start_year

    Returns:
        structure_id: the requested structure id
        period: "start_year-end_year"
        num_found: total number of publications matching the filters in HAL
        total_returned: number of publications actually used to compute stats
        has_more: True if num_found > total_returned — stats below are based on
            a partial sample, not the full set. If True, do not present the
            numbers as exhaustive; mention that they are based on a subset.
        stats: dict of {year: {doc_type: count}}
        query_url: exact URL called (for traceability)
    """
    if start_year > end_year:
        return {"error": f"start_year ({start_year}) doit être <= end_year ({end_year})"}

    try:
        result = await search_publication_stats(
            struct_id=struct_id,
            start_year=start_year,
            end_year=end_year,
        )
    except Exception as e:
        return {"error": f"Erreur inattendue lors de l'appel à HAL : {e}"}

    if "error" in result:
        return {"error": result["error"], "query_url": result.get("query_url")}

    publications = result["publications"]

    stats: dict = {}
    for item in publications:
        year = item["year"] if item["year"] is not None else "UNKNOWN"
        ptype = item["type"] or "UNKNOWN"
        stats.setdefault(year, {})
        stats[year][ptype] = stats[year].get(ptype, 0) + 1

    return {
        "structure_id": struct_id,
        "period": f"{start_year}-{end_year}",
        "num_found": result["num_found"],
        "total_returned": result["total_returned"],
        "has_more": result["has_more"],
        "stats": stats,
        "query_url": result["query_url"],
    }