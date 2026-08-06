import re
from core.mcp import mcp
from hal_api.api_search_author_publications import search_author_publications as _search_author_publications

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


def validate_date(date_str: str | None, field_name: str):
    if date_str is None:
        return
    if not re.match(DATE_PATTERN, date_str):
        raise ValueError(
            f"{field_name} must be in format YYYY-MM-DD, got: {date_str}"
        )


@mcp.tool()
async def search_author_publications(
    author_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    rows: int = 50,
):
    """
        search_author_publications - Recherche les publications d'un auteur dans HAL.

        Utiliser cet outil lorsque l'utilisateur souhaite consulter les publications
        d'un auteur, obtenir leurs métadonnées.

        Parameters:
            author_name: Nom complet de l'auteur (ex. : "Yutong FEI").
            start_date:
                Date de début de la période de recherche (incluse),
                au format YYYY-MM-DD.
                Si None, aucune borne inférieure n'est appliquée.
            end_date:
                Date de fin de la période de recherche (incluse),
                au format YYYY-MM-DD.
                Si None, aucune borne supérieure n'est appliquée.
            rows:
                Nombre maximal de publications à retourner
                (par défaut : 50).

        Returns:
            total:
                Nombre total de publications retournées.
            with_abstract:
                Nombre de publications disposant d'un résumé.
            without_abstract:
                Nombre de publications sans résumé.
            publications:
                Liste des publications avec leurs principales métadonnées,
                notamment :
                - titre ;
                - résumé ;
                - date de publication ;
                - année ;
                - type de document ;
                - DOI (lorsqu'il est disponible).
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
