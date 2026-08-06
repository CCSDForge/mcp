import asyncio
from datetime import date
import aiohttp

BASE_URL = "https://api.archives-ouvertes.fr/search/"


async def search_publication_anr_open_access(
    open_access: bool | None = None,
    struct_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    rows: int = 10,
) -> dict:
    """
    Récupère les publications HAL ayant un financement ANR (anrProject_t non vide).
    Retourne un dict avec le nombre total réel de résultats (numFound), la liste
    des publications effectivement récupérées (limitée par `rows`), et la requête
    Solr réellement envoyée (pour vérification/debug).

    start_date / end_date : bornes de date complète (année-mois-jour), incluses.
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

    if start_date is not None or end_date is not None:
        lower = f"{start_date.isoformat()}T00:00:00Z" if start_date else "*"
        upper = f"{end_date.isoformat()}T23:59:59Z" if end_date else "*"
        fq_parts.append(f"publicationDate_tdate:[{lower} TO {upper}]")

    params = [
        ("q", query),
        ("wt", "json"),
        ("fl", "publicationDateY_i,publicationDate_tdate,docType_s,uri_s,title_s,submitType_s,anrProject_t"),
        ("rows", rows),
        ("sort", "publicationDate_tdate desc"),
    ]
    for fq in fq_parts:
        params.append(("fq", fq))

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(BASE_URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                request_url = str(resp.url)
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
            "publication_date": d.get("publicationDate_tdate"),
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


def build_period_applied(start_date: date | None, end_date: date | None) -> str:
    """
    Construit une chaîne lisible décrivant la période appliquée aux filtres.
    """
    if not start_date and not end_date:
        return "aucune restriction (toutes dates confondues)"
    lower = start_date.isoformat() if start_date else "..."
    upper = end_date.isoformat() if end_date else "..."
    return f"{lower} – {upper}"


async def count_anr_publications_logic(
    open_access: bool | None = None,
    struct_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """
    Calcule le nombre de publications HAL financées par l'ANR correspondant
    aux filtres donnés. uniquement le compte.
    """
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    try:
        result = await search_publication_anr_open_access(
            open_access=open_access,
            struct_id=struct_id,
            start_date=start_date,
            end_date=end_date,
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
        "period_applied": build_period_applied(start_date, end_date),
        "query_url": result["query_url"],
    }