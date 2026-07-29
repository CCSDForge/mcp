import asyncio
import aiohttp

BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_publication_anr_open_access(
    open_access: bool | None = None,
    struct_id: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    rows: int = 10,
) -> dict:
    """
    Récupère les publications HAL ayant un financement ANR (anrProject_t non vide).
    Retourne un dict avec le nombre total réel de résultats (numFound), la liste
    des publications effectivement récupérées (limitée par `rows`), et la requête
    Solr réellement envoyée (pour vérification/debug).
    """
    query_parts = []
    if struct_id is not None:
        query_parts.append(f"structId_i:{struct_id}")
    query = " AND ".join(query_parts) if query_parts else "*:*"

    fq_parts = ["anrProject_t:[* TO *]"]
    if open_access is True:
        fq_parts.append("openAccess_bool:true")
    elif open_access is False:
        fq_parts.append("-openAccess_bool:true")
    # si open_access is None : aucun filtre ajouté

    if start_year is not None or end_year is not None:
        lower = start_year if start_year is not None else "*"
        upper = end_year if end_year is not None else "*"
        fq_parts.append(f"publicationDateY_i:[{lower} TO {upper}]")

    params = [
        ("q", query),
        ("wt", "json"),
        ("fl", "publicationDateY_i,docType_s,uri_s,title_s,submitType_s,anrProject_t"),
        ("rows", rows),
        ("sort", "publicationDateY_i desc"),
    ]
    for fq in fq_parts:
        params.append(("fq", fq))

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(BASE_URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                request_url = str(resp.url)  # URL réellement envoyée, avec encodage final
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return {
            "error": f"Échec de la requête HAL : {e}",
            "num_found": 0,
            "publications": [],
            "query_url": None,
        }

    response = data.get("response", {})
    num_found = response.get("numFound", 0)
    docs = response.get("docs", [])

    publications = [
        {
            "publication_year": d.get("publicationDateY_i"),
            "doc_type": d.get("docType_s"),
            "url": d.get("uri_s"),
            "title": (
                d.get("title_s", [None])[0]
                if isinstance(d.get("title_s"), list)
                else d.get("title_s")
            ),
            "submit_type": d.get("submitType_s"),
            "anr_project": d.get("anrProject_t"),
        }
        for d in docs
    ]

    return {
        "num_found": num_found,
        "publications": publications,
        "query_url": request_url,
    }