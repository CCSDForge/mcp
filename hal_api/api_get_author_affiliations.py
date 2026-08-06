import json
import aiohttp
from collections import Counter

SEARCH_URL = "https://api.archives-ouvertes.fr/search/"

FIELDS_TO_FETCH = (
    "docid,halId_s,title_s,submittedDate_s,"
    "structPrimaryHasAuthIdHal_fs,structHasAuthIdHal_fs"
)


def _parse_struct_auth_entry(entry: str):
    """
    Parse une entrée de type structPrimaryHasAuthIdHal_fs / structHasAuthIdHal_fs :
    "{struct_id}_FacetSep_{struct_name}_JoinSep_{hal_id}_FacetSep_{auth_full_name}"

    Retourne None si le format ne correspond pas à ce qui a été observé
    empiriquement (mieux vaut ignorer une entrée mal formée que deviner).
    """
    if not entry or "_JoinSep_" not in entry:
        return None
    left, right = entry.split("_JoinSep_", 1)
    if "_FacetSep_" not in left or "_FacetSep_" not in right:
        return None
    struct_id, struct_name = left.split("_FacetSep_", 1)
    hal_id_found, auth_name = right.split("_FacetSep_", 1)
    return {
        "struct_id": struct_id,
        "struct_name": struct_name,
        "hal_id": hal_id_found,
        "auth_full_name": auth_name,
    }


async def hal_api_get_author_affiliations(id_hal: str, rows: int = 100) -> dict:
    """
    Récupère les affiliations d'un auteur HAL en interrogeant ses publications
    (collection /search/) et en extrayant + agrégeant les champs de structure
    primaire/secondaire, filtrés strictement sur ce hal_id exact.

    Args:
        id_hal: identifiant HAL de l'auteur (ex: "yutong-fei")
        rows: nombre max de publications à parcourir pour cet auteur

    Returns:
        dict avec :
          num_found, total_returned, has_more : sur le nombre de PUBLICATIONS
            trouvées pour cet auteur (pas directement le nombre d'affiliations)
          raw_docs : liste brute des documents HAL, non modifiée
          raw_fields_sample : noms de champs réellement présents sur le 1er
            doc (calculé dynamiquement, jamais codé en dur)
          primary_structures_by_frequency : liste de
            {struct_id, struct_name, num_publications}, triée par fréquence
            décroissante -- calculée UNIQUEMENT à partir de
            structPrimaryHasAuthIdHal_fs, filtrée sur ce hal_id exact.
            C'est la source la plus fiable pour répondre à "quelle est
            l'affiliation principale de cet auteur".
          all_linked_structures_by_frequency : idem mais à partir de
            structHasAuthIdHal_fs -- ensemble plus large, incluant la
            hiérarchie institutionnelle parente. Plus bruité, à ne présenter
            qu'en complément, jamais comme "l'affiliation principale".
          query_url : URL exacte appelée, pour traçabilité.

        En cas d'échec réseau ou de réponse non-JSON, retourne
        {"error": ..., "query_url": ...}.
    """
    params = {
        "q": f'authIdHal_s:"{id_hal}"',
        "wt": "json",
        "rows": rows,
        "fl": FIELDS_TO_FETCH,
    }

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(SEARCH_URL, params=params) as resp:
                query_url = str(resp.url)

                if resp.status != 200:
                    return {
                        "error": f"L'API HAL a répondu avec le code {resp.status}",
                        "query_url": query_url,
                    }

                content_type = resp.headers.get("Content-Type", "")
                text = await resp.text()

                looks_like_html = text.lstrip()[:20].lower().startswith(("<!doctype", "<html"))
                if "html" in content_type.lower() or looks_like_html:
                    return {
                        "error": (
                            "L'API HAL a renvoyé du HTML au lieu du JSON attendu. "
                            "L'endpoint ou les paramètres sont probablement incorrects."
                        ),
                        "query_url": query_url,
                    }

                try:
                    data = json.loads(text)
                except json.JSONDecodeError as e:
                    return {"error": f"Réponse HAL non-JSON : {e}", "query_url": query_url}

    except aiohttp.ClientError as e:
        return {"error": f"Erreur réseau lors de l'appel à l'API HAL : {e}", "query_url": None}
    except Exception as e:
        return {"error": f"Erreur inattendue lors de l'appel à l'API HAL : {e}", "query_url": None}

    response_block = data.get("response", {})
    docs = response_block.get("docs", [])
    num_found = response_block.get("numFound", len(docs))

    # FIX anti-hallucination : les champs disponibles sont lus dynamiquement
    # depuis la vraie réponse, jamais supposés ou codés en dur.
    raw_fields_sample = list(docs[0].keys()) if docs else []

    primary_counter = Counter()
    all_counter = Counter()
    struct_name_lookup = {}

    for doc in docs:
        for entry in (doc.get("structPrimaryHasAuthIdHal_fs") or []):
            parsed = _parse_struct_auth_entry(entry)
            # On ne garde que les entrées qui correspondent EXACTEMENT à ce
            # hal_id -- essentiel si le document a plusieurs co-auteurs.
            if parsed and parsed["hal_id"] == id_hal:
                key = parsed["struct_id"]
                primary_counter[key] += 1
                struct_name_lookup[key] = parsed["struct_name"]

        for entry in (doc.get("structHasAuthIdHal_fs") or []):
            parsed = _parse_struct_auth_entry(entry)
            if parsed and parsed["hal_id"] == id_hal:
                key = parsed["struct_id"]
                all_counter[key] += 1
                struct_name_lookup.setdefault(key, parsed["struct_name"])

    primary_structures_by_frequency = [
        {"struct_id": sid, "struct_name": struct_name_lookup.get(sid), "num_publications": count}
        for sid, count in primary_counter.most_common()
    ]
    all_linked_structures_by_frequency = [
        {"struct_id": sid, "struct_name": struct_name_lookup.get(sid), "num_publications": count}
        for sid, count in all_counter.most_common()
    ]

    return {
        "num_found": num_found,
        "total_returned": len(docs),
        "has_more": num_found > len(docs),
        "raw_docs": docs,
        "raw_fields_sample": raw_fields_sample,
        "primary_structures_by_frequency": primary_structures_by_frequency,
        "all_linked_structures_by_frequency": all_linked_structures_by_frequency,
        "query_url": query_url,
    }