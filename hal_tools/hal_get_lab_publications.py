from collections import Counter
from core.mcp import mcp
from hal_api.search_lab_publications import search_lab_publications


def _compute_yearly_distribution(publications: list[dict]) -> dict[str, int]:
    """Calcule le nombre de publications par année """
    counts: dict[str, int] = {}
    for pub in publications:
        if year := pub.get("year"):
            counts[year] = counts.get(year, 0) + 1
    return dict(sorted(counts.items()))


def _compute_type_distribution(publications: list[dict]) -> dict[str, int]:
    """Calcule la distribution des types de documents."""
    types = [pub["type"] for pub in publications if pub.get("type")]
    return dict(Counter(types).most_common())


@mcp.tool()
async def hal_get_lab_publications(
    structure_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    rows: int = 200,
) -> dict:
    """
    Analyse l'activité de recherche d'une structure scientifique sur HAL.

    Récupère les publications et effectue une agrégation bibliométrique incluant :
    - le nombre total de publications
    - la distribution annuelle de la production scientifique
    - la distribution par type de document (article, thèse, communication, etc.)
    - les métadonnées structurées (titre, résumé, mots-clés, DOI)

    Conçu pour l'analyse de tendances scientifiques, le suivi de la recherche,
    et l'analyse temporelle de la production d'une structure dans HAL.

    Args:
        structure_id: Identifiant HAL de la structure (structId_s).
        start_date: Date de début au format ISO (ex: '2020-01-01').
        end_date: Date de fin au format ISO (ex: '2023-12-31').
        rows: Nombre maximum de publications à récupérer (défaut: 200).

    Returns:
        Dictionnaire contenant les métadonnées agrégées et la liste des publications.
    """
    publications = await search_lab_publications(
        structure_id=structure_id,
        start_date=start_date,
        end_date=end_date,
        rows=rows,
    )

    return {
        "structure_id": structure_id,
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "total_publications": len(publications),
        "by_year": _compute_yearly_distribution(publications),
        "by_type": _compute_type_distribution(publications),
        "publications": publications,
    }