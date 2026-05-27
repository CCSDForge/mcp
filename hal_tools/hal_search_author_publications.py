import re
from core.mcp import mcp
from hal_api.search_author_publications import search_author_publications as _search_author_publications

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


def validate_date(date_str: str | None, field_name: str):
    if date_str is None:
        return
    if not re.match(DATE_PATTERN, date_str):
        raise ValueError(
            f"{field_name} must be in format YYYY-MM-DD, got: {date_str}"
        )


@mcp.tool()
async def hal_search_author_publications(
    author_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    rows: int = 50,
):
    """
    Search publications by author name in HAL.

    Returns:
        title, abstract, year, document type, DOI.

    Parameters:
        author_name: Full author name (e.g. 'Yutong FEI')
        start_date: filter start date (YYYY-MM-DD)
        end_date: filter end date (YYYY-MM-DD)
        rows: maximum number of results (default: 50)
    """

    validate_date(start_date, "start_date")
    validate_date(end_date, "end_date")

    publications = await _search_author_publications(
        author_name=author_name,
        start_date=start_date,
        end_date=end_date,
        rows=rows,
    )

    with_abstract = [
        p for p in publications
        if p.get("abstract") and p["abstract"] != "Pas de résumé disponible"
    ]

    return {
        "total": len(publications),
        "with_abstract": len(with_abstract),
        "without_abstract": len(publications) - len(with_abstract),
        "publications": publications,
    }
