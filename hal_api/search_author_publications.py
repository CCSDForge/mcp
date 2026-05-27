import aiohttp
from typing import Optional

BASE_URL = "https://api.archives-ouvertes.fr/search/"

def extract_year(date_str: str | None) -> int | None:
    if not date_str:
        return None
    return int(date_str[:4])

async def search_author_publications(
    author_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    rows: int = 50,
) -> list[dict]:
    start_year = extract_year(start_date)
    end_year = extract_year(end_date)

    params: dict = {
    "q": f'"{author_name}"',
    "fl": "title_s,abstract_s,producedDateY_i,producedDate_s,docType_s,doiId_s", 
    "rows": rows,
    }

    # Correction : gère les 3 cas (start seul, end seul, les deux)
    if start_year or end_year:
        low = str(start_year) if start_year else "*"
        high = str(end_year) if end_year else "*"
        params["fq"] = f"producedDateY_i:[{low} TO {high}]"

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    docs = data.get("response", {}).get("docs", [])
    results = []
    for d in docs:
        title = d.get("title_s")
        if isinstance(title, list):
            title = title[0]

        abstract = d.get("abstract_s")
        if isinstance(abstract, list):
            abstract = abstract[0]
        if not abstract:
            abstract = "Pas de résumé disponible"
            
        results.append({
            "title": title,
            "abstract": abstract,
            "year": d.get("producedDateY_i"),
            "date": d.get("producedDate_s"),   # ← date complète ex: "2023-06-15"
            "type": d.get("docType_s"),
            "doi": d.get("doiId_s"),
        })

    return results
