import aiohttp
from typing import Optional

BASE_URL = "https://api.archives-ouvertes.fr/search/"

HAL_FIELDS = [
    "title_s",
    "abstract_s",
    "keyword_s",
    "authFullName_s",
    "producedDateY_i",
    "producedDate_s",
    "docType_s",
    "doiId_s",
    "structId_i",
]


def _extract_year(date_str: str | None) -> int | None:
    if not date_str:
        return None

    try:
        return int(date_str[:4])
    except (ValueError, TypeError):
        return None


def _first_or_none(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _join_list(value):
    if isinstance(value, list):
        return " ".join(value) if value else None
    return value


def _normalize_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _build_query_params(structure_id, start_year, end_year, rows):
    fq_parts = [f"structId_i:{structure_id}"]

    if start_year or end_year:
        low = str(start_year) if start_year else "*"
        high = str(end_year) if end_year else "*"

        fq_parts.append(
            f"producedDateY_i:[{low} TO {high}]"
        )

    return {
        "q": "*:*",
        "rows": rows,
        "fl": ",".join(HAL_FIELDS),
        "fq": " AND ".join(fq_parts),
        "wt": "json",
    }


def _parse_document(raw: dict) -> dict:
    return {
        "title": _first_or_none(raw.get("title_s")),

        "abstract": (
            _first_or_none(raw.get("abstract_s"))
            or "No abstract available"
        ),

        "keywords": _normalize_list(raw.get("keyword_s")),

        "authors": _normalize_list(raw.get("authFullName_s")),

        "year": raw.get("producedDateY_i"),

        "date": raw.get("producedDate_s"),

        "type": raw.get("docType_s"),

        "doi": raw.get("doiId_s"),

        "structure_id": raw.get("structId_i"),
    }


async def search_lab_publications(
    structure_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    rows: int = 200,
) -> list[dict]:

    params = _build_query_params(
        structure_id=structure_id,
        start_year=_extract_year(start_date),
        end_year=_extract_year(end_date),
        rows=rows,
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as response:
            response.raise_for_status()

            print("Request URL:", response.url)

            data = await response.json(content_type=None)

    raw_docs = data.get("response", {}).get("docs", [])

    return [_parse_document(doc) for doc in raw_docs]