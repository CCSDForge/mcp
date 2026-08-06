from core.mcp import mcp
from hal_api.api_search_structures import hal_api_search_structure as _search_structure


@mcp.tool()
async def search_structures(
    nom_structure: str,
    rows: int = 50,
):
    """
    search_structure - Recherche des structures de recherche référencées dans HAL
    (laboratoires, universités, institutions, organismes de recherche, etc.) à
    partir de leur nom ou de leur acronyme.

    UTILISER CET OUTIL lorsque l'utilisateur souhaite :
      - identifier une structure de recherche dans HAL ;
      - récupérer son identifiant HAL (`struct_id`) ;
      - retrouver la structure parente d'un laboratoire ou d'une équipe de recherche ;
      - rechercher une structure à partir d'un nom complet, d'un acronyme ou d'un
        nom partiel (ex. : "Lyon 1", "CNRS", "LIP6").

    L'outil gère les recherches approximatives ou partielles. Par exemple,
    « Lyon 1 » permet de retrouver « Université Claude Bernard Lyon 1 ».

    Les structures sont classées selon leur statut de validation (`statut_validation`) :

      - `VALID` :
        Structure officiellement validée dans HAL. Son identifiant peut être utilisé
        comme référence dans les autres outils.

      - `INCOMING` :
        Structure enregistrée mais non encore validée. Son identifiant peut évoluer
        ou être fusionné avec une autre structure.

      - Autres statuts :
        Cas plus rares ou hérités ; ils doivent être interprétés avec prudence.

    IMPORTANT - Règles anti-hallucination :
      - Ne rapporter que les identifiants, noms et statuts de validation
        explicitement présents dans :
          * `structures_valides`
          * `structures_incoming`
          * `structures_autres_statuts`

      - Ne jamais inventer ou déduire un identifiant HAL à partir de connaissances
        générales, même si la structure est connue.
      - Toujours préciser si un identifiant provient d'une structure `VALID`
        ou `INCOMING`. Ne jamais présenter une structure `INCOMING` comme étant
        officiellement validée.
      - Si `num_found` est égal à 0, indiquer explicitement qu'aucune structure
        correspondante n'a été trouvée.
      - Si `has_more` est égal à `True`, cela signifie que tous les résultats
        n'ont pas été récupérés (`num_found > total_returned`).
        Ne pas conclure qu'une structure est absente ou non validée sur la base
        d'une liste incomplète. Relancer l'outil avec une valeur de `rows`
        plus élevée (voir le champ `warning`) avant de tirer une conclusion.

    Parameters:
        nom_structure: Nom, acronyme ou fragment du nom de la structure à rechercher (ex. : "Lyon 1", "CNRS", "LIP6").
        rows: Nombre maximal de structures à retourner (par défaut : 50).

    Returns:
        num_found: Nombre total de structures correspondant à la recherche dans HAL.
        total_returned: Nombre de structures effectivement retournées.
        has_more: Vaut `True` si tous les résultats n'ont pas été récupérés (`num_found > total_returned`).
        structures: Liste complète des structures retournées, tous statuts confondus.
        structures_valides: Sous-ensemble des structures dont le statut est `VALID`.
        structures_incoming: Sous-ensemble des structures dont le statut est `INCOMING`.
        structures_autres_statuts: Sous-ensemble des structures ayant un autre statut de validation.
        query_url: URL exacte de la requête envoyée à l'API HAL.
    """

    if not nom_structure or not nom_structure.strip():
        return {"error": "Le paramètre 'nom_structure' est requis et ne peut pas être vide"}

    rows = max(1, rows)

    try:
        result = await _search_structure(nom_structure=nom_structure.strip(), rows=rows)
    except Exception as e:
        return {"error": f"Erreur inattendue lors de l'appel à HAL : {e}"}

    if "error" in result:
        return {"error": result["error"], "query_url": result.get("query_url")}

    structures = result["structures"]
    num_found = result["num_found"]
    total_returned = len(structures)
    has_more = num_found > total_returned

    response = {
        "num_found": num_found,
        "total_returned": total_returned,
        "has_more": has_more,
        "structures": structures,
        "structures_valides": result["structures_valides"],
        "structures_incoming": result["structures_incoming"],
        "structures_autres_statuts": result["structures_autres_statuts"],
        "query_url": result["query_url"],
    }

    if has_more:
        response["warning"] = (
            f"Seuls {total_returned} résultats sur {num_found} ont été récupérés. "
            f"Relance cet outil avec un paramètre 'rows' plus élevé (ex: rows={num_found}) "
            f"pour obtenir la liste complète avant de conclure sur l'absence d'une structure."
        )

    return response