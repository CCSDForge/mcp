import httpx

DEHAL_STRUCTURE_URL = "https://api.archives-ouvertes.fr/ref/structure/"
FIELDS = "docid,label_s,acronym_s,type_s,parentDocid_s,parentName_s,valid_s"


def _to_structure(doc: dict) -> dict:
    return {
        "id": doc.get("docid"),
        "nom": doc.get("label_s"),
        "sigle": doc.get("acronym_s"),
        "type": doc.get("type_s"),
        "id_parent": doc.get("parentDocid_s"),
        "nom_parent": doc.get("parentName_s"),
        "statut_validation": doc.get("valid_s"),  # ex: "VALID", "INCOMING"
    }


async def hal_api_search_structure(
    nom_structure: str,
    rows: int = 10,
) -> dict:
    """
    Interroge l'API deHAL /ref/structure pour rechercher une structure par nom ou sigle.

    Args:
        nom_structure: nom ou sigle recherché (ex: "Lyon 1", "CNRS", "IP Paris")
        rows: nombre maximum de résultats retournés par HAL

    Returns:
        dict avec:
            - num_found (int): nombre total de structures correspondantes côté HAL
            - structures (list[dict]): structures retournées, détaillées
            - structures_valides / structures_incoming / structures_autres_statuts
            - query_url (str): url exacte appelée (utile pour debug/traçabilité)
    """
    params = {
        "q": f'text:"{nom_structure}"',
        "fl": FIELDS,
        "rows": rows,
        "wt": "json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(DEHAL_STRUCTURE_URL, params=params)

    query_url = str(response.url)
    if response.status_code != 200:
        return {
            "error": f"L'API deHAL a répondu avec le code {response.status_code}",
            "query_url": query_url,
        }

    data = response.json()
    resp = data.get("response", {})
    docs = resp.get("docs", [])
    num_found = resp.get("numFound", len(docs))

    structures = [_to_structure(doc) for doc in docs]
    structures_valides = [s for s in structures if s["statut_validation"] == "VALID"]
    structures_incoming = [s for s in structures if s["statut_validation"] == "INCOMING"]
    structures_autres = [
        s for s in structures
        if s["statut_validation"] not in ("VALID", "INCOMING")
    ]

    return {
        "num_found": num_found,
        "structures": structures,
        "structures_valides": structures_valides,
        "structures_incoming": structures_incoming,
        "structures_autres_statuts": structures_autres,
        "query_url": query_url,
    }


async def hal_api_get_structure_by_id(structure_id) -> dict:
    """
    Interroge l'API deHAL /ref/structure pour résoudre un structure_id
    (docid numérique, ex: structId_i sur les publications) vers son nom
    lisible et ses métadonnées. Complément de hal_api_search_structure, qui
    cherche par nom/sigle plutôt que par id exact.

    Args:
        structure_id: identifiant numérique de la structure (docid), ex:
            194495 pour Université Claude Bernard Lyon 1.

    Returns:
        dict avec:
            - found (bool)
            - structure (dict | None): {id, nom, sigle, type, id_parent,
              nom_parent, statut_validation} si trouvé
            - num_found (int)
            - query_url (str)
    """
    params = {
        "q": f"docid:{structure_id}",
        "fl": FIELDS,
        "rows": 1,
        "wt": "json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(DEHAL_STRUCTURE_URL, params=params)

    query_url = str(response.url)
    if response.status_code != 200:
        return {
            "error": f"L'API deHAL a répondu avec le code {response.status_code}",
            "query_url": query_url,
        }

    data = response.json()
    resp = data.get("response", {})
    docs = resp.get("docs", [])
    num_found = resp.get("numFound", len(docs))

    if not docs:
        return {
            "found": False,
            "structure": None,
            "num_found": num_found,
            "query_url": query_url,
        }

    return {
        "found": True,
        "structure": _to_structure(docs[0]),
        "num_found": num_found,
        "query_url": query_url,
    }