from core.mcp import mcp
from hal_api.api_get_publication_statistics_by_structure import search_publication_stats


@mcp.tool()
async def get_publication_statistics_by_structure(
    struct_id: int,
    start_year: int,
    end_year: int,
):
    """
    Outil get_publication_statistics_by_structure - Récupère le nombre de publications HAL pour une structure et une
    période données, réparties par année et par type de document.

    Utiliser cet outil lorsque l'utilisateur souhaite connaître la production scientifique d'une structure (laboratoire,
    université, institution, etc.), notamment le nombre de publications par année et leur répartition par type de document.

    IMPORTANT :
    Cet outil nécessite l'identifiant HAL (`struct_id`) de la structure.
    Si l'utilisateur ne connaît que le nom ou l'acronyme de la structure,
    utiliser d'abord l'outil `search_structures` afin de récupérer son
    identifiant HAL, puis appeler cet outil avec le `struct_id` obtenu.

    Parameters:
        - struct_id: Identifiant HAL de la structure de recherche.
        - start_year: Année de début de la période d'analyse (incluse).
        - end_year: Année de fin de la période d'analyse (incluse). Doit être supérieure ou égale à `start_year`.

    Returns:
        - structure_id: Identifiant HAL de la structure analysée.
        - period: Période analysée au format "start_year-end_year".
        - num_found: Nombre total de publications correspondant aux critères dans HAL.
        - total_returned: Nombre de publications effectivement utilisées pour calculer les statistiques.
        - has_more: Indique si toutes les publications n'ont pas été récupérées
            (`num_found > total_returned`). Si cette valeur est `True`, les statistiques
            sont calculées sur un sous-ensemble des publications et ne doivent pas être
            présentées comme exhaustives.
        - stats: Répartition des publications par année et par type de document, sous la forme :
            `{année: {type_document: nombre_de_publications}}`.
        - query_url: URL de la requête envoyée à l'API HAL, fournie à des fins de traçabilité.
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