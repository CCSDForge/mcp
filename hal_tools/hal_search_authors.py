from hal_api.search_authors import search_authors
from core.mcp import mcp


@mcp.tool()
async def hal_search_authors(query: str, rows: int = 10):
    authors = await search_authors(query, rows=rows)
    """
    Search authors in the HAL referential.
    Returns their name, HAL id, docid and affiliated structure.

    Args:
        query: author name or fragment to search for.
        rows:  maximum number of results (default: 10).
    """
    return {
        "total": len(authors),
        "authors": authors,
    }
