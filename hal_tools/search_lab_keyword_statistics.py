from core.mcp import mcp
from hal_api.api_search_lab_keyword_statistics import search_lab_keywords


@mcp.tool()
async def search_lab_keyword_statistics(
    structure_id: str,
    year: int
) -> dict:
    """
    search_lab_keyword_statistics - Analyse les thématiques de recherche d'une structure enregistrée dans HAL à partir de la distribution des mots-clés de ses publications.

    UTILISER CET OUTIL lorsque l'utilisateur souhaite :
      - identifier les thématiques de recherche ou les thématiques émergentes d'une structure ;
      - connaître les mots-clés les plus fréquents des publications d'une structure pour une année donnée ;
      - analyser les principaux sujets de recherche d'un laboratoire, d'une université ou d'une institution.

    IMPORTANT :
      - Cet outil ne retourne PAS la liste des publications.
      - Les statistiques sont calculées directement par Solr à l'aide des facettes (`facet`).
      - Le champ `keyword_aggregation` contient déjà les fréquences des mots-clés.
      - Le LLM ne doit effectuer aucun comptage ou recalcul des occurrences.

    Workflow :
      1. Si l'utilisateur fournit uniquement le nom ou l'acronyme d'une structure,
         utiliser d'abord `search_structure` afin de récupérer son identifiant HAL (`structure_id`).
      2. Appeler ensuite cet outil avec `structure_id` et l'année souhaitée.

    Parameters:
        - structure_id: Identifiant HAL de la structure de recherche.
        - year: Année des publications à analyser.
        - limit: Nombre maximal de mots-clés à retourner (par défaut : 30).

    Returns:
        - structure_id: Identifiant HAL de la structure analysée.
        - year: Année analysée.
        - total_publications: Nombre total de publications de la structure pour cette année.
        - keyword_aggregation: Agrégation des mots-clés, sous la forme :
            `{mot_clé: nombre_d'occurrences}`,
            classés par fréquence décroissante.
    """

    result = await search_lab_keywords(
        structure_id,
        year
    )


    return result