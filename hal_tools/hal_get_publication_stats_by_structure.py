from core.mcp import mcp
from hal_api.search_publication_stats import search_publication_stats
from typing import Annotated
from pydantic import Field

@mcp.tool()
async def hal_get_publication_stats_by_structure(
    struct_id: int,
    start_year: Annotated[
        int,
        Field(
            ge=1980,
            le=2030,
            description="Start year (1980-2030)"
        )
    ],
    end_year: Annotated[
        int,
        Field(
            ge=2020,
            le=2025,
            description="End year (1980-2030)"
        )
    ],
):
    """
    Get number of publications from HAL by year and type
    for a given structure and period.
    """

    data = await search_publication_stats(
        struct_id=struct_id,
        start_year = start_year, 
        end_year=end_year
    )

    # aggregation finale propre
    stats = {}

    for item in data:
        year = item["year"]
        ptype = item["type"] or "UNKNOWN"

        if year not in stats:
            stats[year] = {}

        if ptype not in stats[year]:
            stats[year][ptype] = 0

        stats[year][ptype] += 1

    return {
        "structure_id": struct_id,
        "period": f"{start_year}-{end_year}",
        "stats": stats
    }

