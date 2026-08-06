from core.mcp import mcp
from hal_api.api_search_authors import search_authors as _search_author
from hal_api import api_get_author_affiliations as _get_author_affiliations


@mcp.tool()
async def get_author_affiliations(
    nom_auteur: str,
    rows: int = 100,
):
    """
    get_author_affiliations - Recherche l'historique des affiliations d'un auteur dans HAL :
    les structures (laboratoires, universités, institutions...) auxquelles il a été
    rattaché, afin d'aider à retracer son évolution de carrière scientifique.

    UTILISER CET OUTIL lorsque l'utilisateur demande :
      - des informations sur les affiliations d'un auteur
      - l'historique des affiliations d'un auteur
      - le laboratoire, l'université ou la structure de rattachement d'un chercheur
      - l'évolution de carrière, le parcours scientifique d'un chercheur
      - "quel laboratoire ?", "quelle université ?", "où travaille ?" un auteur

    Attention : NE PAS utiliser cet outil pour rechercher les PUBLICATIONS d'un auteur
    (articles, thèses, communications, etc.). Utiliser un outil de recherche de
    publications dédié comme search_author_publication.
    L'outil get_author_affiliations retourne uniquement les relations auteur-structure/affiliation et non la liste des publications.

    Fonctionnement : identifie l'auteur (hal_id) par outil search_authors puis extrait, depuis ses notices de publication HAL, deux champs :
        - structPrimaryHasAuthIdHal_fs : affiliation principale déclarée par publication
        - structHasAuthIdHal_fs : toutes les structures associées (principales + secondaires + hiérarchie institutionnelle) — plus large, plus bruité
        Les occurrences de structPrimaryHasAuthIdHal_fs sont agrégées dans primary_structures_by_frequency.

    RÈGLES ANTI-HALLUCINATION (strictes) :
         - Ne rapporter que ce qui est présent dans primary_structures_by_frequency, all_linked_structures_by_frequency ou raw_docs. Jamais d'invention de nom, id ou période à partir de connaissances générales.
         - Pour une affiliation "principale"/"actuelle" : utiliser primary_structures_by_frequency (all_linked... est trop large/parent).
         - Ne jamais déduire une affiliation depuis un titre ou un résumé de publication.
         - Pas de notion d'"affiliation implicite" : une affiliation est présente dans les données ou inconnue.
         - Toujours formuler comme "structure apparaissant comme affiliation principale déclarée dans X publications", jamais comme un fait certifié d'"affiliation actuelle".
         - Homonymes (plusieurs auteurs dans authors_found) : présenter séparément ou demander confirmation, ne jamais fusionner.
         - num_found = 0, pas d'affiliation, pas de hal_id, has_more=true, ou clé "error" dans affiliations_by_author : signaler tel quel, sans reconstruire ni estimer.

    Paramétrage :
        - nom_auteur: nom de l'auteur à rechercher (ex: "Jean Dupont")
        - rows: nombre max d'enregistrements d'affiliation par auteur (défaut: 100)

    Returns:
        authors_found: [{name, hal_id, docid, statut_validation}, ...]
        homonyms_warning: présent si plusieurs auteurs correspondent au nom
        affiliations_by_author: {
            hal_id: {
                num_found, total_returned, has_more, raw_docs, raw_fields_sample,
                primary_structures_by_frequency, all_linked_structures_by_frequency
            }
            # ou {"error": "..."} en cas d'échec pour cet auteur
        }
        query_url_author_search: URL utilisée pour identifier l'auteur dans HAL
"""
    if not nom_auteur or not nom_auteur.strip():
        return {"error": "Le paramètre 'nom_auteur' est requis et ne peut pas être vide"}

    try:
        author_result = await _search_author(nom_auteur.strip())
    except Exception as e:
        return {"error": f"Erreur inattendue lors de la résolution de l'auteur : {e}"}

    if "error" in author_result:
        return {"error": author_result["error"], "query_url": author_result.get("query_url")}

    authors = author_result["authors"]

    if not authors:
        return {
            "authors_found": [],
            "message": f"Aucun auteur trouvé pour '{nom_auteur}' dans HAL.",
            "query_url_author_search": author_result["query_url"],
        }

    response = {
        "authors_found": authors,
        "query_url_author_search": author_result["query_url"],
    }

    if len(authors) > 1:
        response["homonyms_warning"] = (
            f"{len(authors)} auteurs correspondent à '{nom_auteur}'. "
            f"Vérifie avec l'utilisateur de qui il s'agit avant de conclure, "
            f"ou présente les affiliations séparément pour chaque personne."
        )

    affiliations_by_author = {}
    for idx, author in enumerate(authors):
        # FIX: la clé produite par hal_search_authors est "hal_id", pas "id_hal".
        # Avant ce fix, cette ligne renvoyait toujours None et l'auteur était
        # silencieusement ignoré (voir le "continue" ci-dessous), ce qui
        # laissait affiliations_by_author vide sans jamais le signaler.
        hal_id = author.get("hal_id")

        if not hal_id:
            # FIX: ne jamais "continue" silencieusement. Un auteur sans hal_id
            # doit produire une entrée d'erreur explicite, distincte d'un
            # "aucune affiliation trouvée", pour que le LLM ne confonde pas
            # "données absentes" avec "erreur technique".
            fallback_key = author.get("name") or f"unknown_author_{idx}"
            affiliations_by_author[fallback_key] = {
                "error": (
                    "Aucun hal_id disponible pour cet auteur (champ 'hal_id' "
                    "manquant ou vide dans les résultats de recherche). "
                    "Les affiliations n'ont pas pu être récupérées."
                )
            }
            continue

        try:
            affil_result = await _get_author_affiliations(id_hal=hal_id, rows=rows)
        except Exception as e:
            affiliations_by_author[hal_id] = {"error": f"Erreur inattendue : {e}"}
            continue

        affiliations_by_author[hal_id] = affil_result

    response["affiliations_by_author"] = affiliations_by_author

    return response