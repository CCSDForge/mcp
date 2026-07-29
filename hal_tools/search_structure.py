from core.mcp import mcp
from hal_api.hal_api_search_structure import hal_api_search_structure as _search_structure


@mcp.tool()
async def search_structure(
    nom_structure: str,
    rows: int = 50,
):
    """
    Search HAL structures (laboratories, universities, research organizations...)
    by name or acronym.

    Use this tool when the user wants to identify a structure, find its HAL id,
    or explore its parent structure (e.g. a lab attached to a university).
    Handles approximate/partial names (e.g. "Lyon 1" matches "Université Claude
    Bernard Lyon 1").

    Structures are grouped by validation status ("statut_validation" field):
      - "VALID": officially validated structure, safe to use as a reference ID
      - "INCOMING": submitted but not yet validated, may change or be merged/renamed
      - other values: rare/legacy statuses, treat with caution

    IMPORTANT — anti-hallucination rule:
      - Only report structure IDs, names, or statuses that are explicitly present
        in the returned lists below (structures_valides, structures_incoming,
        structures_autres_statuts).
      - Never guess, infer, or recall a structure ID from prior/general knowledge,
        even if it seems "standard" or well-known.
      - Clearly tell the user whether an ID comes from a VALID or an INCOMING
        structure — do not present an INCOMING id as if it were validated.
      - If num_found is 0 or no structure matches what the user asked for, say so
        explicitly instead of providing an unverified ID.
      - If "has_more" is true, this means num_found > total_returned: more matching
        structures exist in HAL than were retrieved. Do NOT conclude that a
        structure "does not exist" or "is not validated" based on a partial list.
        Re-call this tool with a higher "rows" value (see the "warning" field)
        before drawing any conclusion.

    Parameters:
        nom_structure: name or acronym to search for (e.g. "Lyon 1", "CNRS", "LIP6")
        rows: maximum number of matching structures to return (default: 50)

    Returns:
        num_found: total number of matching structures in HAL
        total_returned: number of structures actually returned
        has_more: true if num_found > total_returned (results were truncated)
        structures: full list of matching structures (all statuses combined)
        structures_valides: subset with statut_validation == "VALID"
        structures_incoming: subset with statut_validation == "INCOMING"
        structures_autres_statuts: subset with any other status value
        query_url: exact URL called (for traceability)
        warning: present only if has_more is true, tells the model to retry with
            a higher rows value
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