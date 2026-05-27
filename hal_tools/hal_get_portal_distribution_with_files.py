from core.mcp import mcp
from hal_api.search_portal_distribution import search_portal_distribution

@mcp.tool()
async def hal_get_portal_distribution_with_files(
    struct_ids: int | list[int],
    year: int,
    top_n: int = 20
):
    """
    Get distribution of HAL deposits by portal for one or multiple structures.
    """

    import asyncio

    # normalisation
    if isinstance(struct_ids, int):
        struct_ids = [struct_ids]

    total, with_file = await asyncio.gather(
        search_portal_distribution(struct_ids, year, False),
        search_portal_distribution(struct_ids, year, True)
    )

    results = []

    for portal, total_count in total.items():
        file_count = with_file.get(portal, 0)
        no_file_count = total_count - file_count

        proportion = (file_count / total_count) if total_count > 0 else 0

        results.append({
            "portal": portal,
            "total": total_count,
            "with_file": file_count,
            "without_file": no_file_count,
            "file_ratio": round(proportion, 3)
        })

    results = sorted(results, key=lambda x: x["total"], reverse=True)[:top_n]

    return {
        "structure_ids": struct_ids,
        "year": year,
        "portals": results
    }