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
    Compte le nombre de publications HAL financées par l'ANR, sans les récupérer.
    Utiliser ce tool pour toute question de type "combien de publications ANR...".

    Parameters:
        open_access: filtre sur le statut open access (True/False/None = pas de filtre)
        struct_id: id de structure HAL pour restreindre à une institution
        start_date: date de début (incluse), format année-mois-jour. None = pas de borne inférieure
        end_date: date de fin (incluse), format année-mois-jour. None = pas de borne supérieure
    """
    return await count_anr_publications_logic(
        open_access=open_access,
        struct_id=struct_id,
        start_date=start_date,
        end_date=end_date,
    )