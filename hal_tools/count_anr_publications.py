from datetime import date
from core.mcp import mcp
from hal_api.api_count_anr_publications import count_anr_publications_logic


@mcp.tool()
async def count_anr_publications(
    open_access: bool | None = None,
    struct_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    """
    Outil count_anr_publications consiste à compter le nombre de publications HAL financées par des projets ANR sans récupérer la liste complète des publications.

    Utiliser cet outil pour répondre aux questions concernant le volume de publications financées par l'ANR, notamment :
    - "Quel est le nombre de publications financées par l'ANR pour une structure donnée ?"
    - "Quelle est la part des publications financées par l'ANR disponibles en accès ouvert pour une structure donnée ?"

    Paramètrage:
        open_access:
            Filtre selon le statut d'accès ouvert des publications.
            True : uniquement les publications en accès ouvert.
            False : uniquement les publications non disponibles en accès ouvert.
            None : aucun filtre appliqué.

        struct_id:
            Identifiant HAL de la structure de recherche (laboratoire, institution,
            université, etc.) pour laquelle les publications ANR doivent être comptées.

        start_date:
            Date de début incluse de la période d'analyse, au format YYYY-MM-DD.
            None : aucune borne inférieure.

        end_date:
            Date de fin incluse de la période d'analyse, au format YYYY-MM-DD.
            None : aucune borne supérieure.

    Returns:
        Retourne les statistiques agrégées concernant :
        - le nombre total de publications financées par l'ANR ;
        - la répartition selon le statut d'accès ouvert lorsque le filtre est utilisé ;
        - les informations de traçabilité de la requête solr API.
    """
    return await count_anr_publications_logic(
        open_access=open_access,
        struct_id=struct_id,
        start_date=start_date,
        end_date=end_date,
    )