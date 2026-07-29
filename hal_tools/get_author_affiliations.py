from core.mcp import mcp
from hal_api.search_authors import search_authors as _search_author
from hal_api import hal_api_get_author_affiliations as _get_author_affiliations


@mcp.tool()
async def get_author_affiliations(
    nom_auteur: str,
    rows: int = 100,
):
    """
    Find an author's affiliation history in HAL: which structures (labs,
    universities...) they have been linked to, to help trace career evolution.

    USE THIS TOOL when the user asks about (in English OR French):
      - "affiliation(s)", "affiliation history", "which lab/university"
      - "affiliation", "affiliations", "structure(s) de rattachement"
      - "évolution de carrière", "carrière", "parcours" of a researcher
      - "quel laboratoire", "quelle université", "où travaille" un auteur
      - a question relating an author to a structure/lab/university over time

    DO NOT use this tool to search for an author's PUBLICATIONS (their papers,
    articles, thesis). Use a publication-search tool for that instead — this
    tool only returns structure/affiliation relations, not publication lists.

    Two-step process:
      1. Resolve the author name to one or more HAL author ids (hal_id).
         If multiple homonyms are found, ALL of them are returned separately —
         do not silently pick one and present it as "the" author.
      2. For each resolved hal_id, fetch the raw author-structure relations.

    IMPORTANT — how this data is actually obtained:
      There is NO dedicated "/search/authorstructure/" endpoint in the HAL
      API (verified empirically: it returns an HTML page, not JSON). HAL does
      not expose a single "current affiliation" field either. Instead, this
      tool queries the author's PUBLICATIONS (the standard /search/
      collection) and extracts two fields present on each publication doc:
        - structPrimaryHasAuthIdHal_fs: structure(s) declared as this
          author's PRIMARY affiliation on that specific publication.
        - structHasAuthIdHal_fs: ALL structures linked to this author on that
          publication, including the parent institutional hierarchy of their
          lab (e.g. a lab's supervising universities) — a broader, noisier set.
      This tool aggregates structPrimaryHasAuthIdHal_fs across ALL of the
      author's publications and counts how often each structure appears,
      producing "primary_structures_by_frequency". Structures appearing most
      often are a good approximation of the author's main/current
      affiliation(s), but this is a DERIVED, COMPUTED signal — not a fact
      literally stated by HAL as "current affiliation".

    IMPORTANT — anti-hallucination rules:
      - Only report structures that are explicitly present in
        "primary_structures_by_frequency", "all_linked_structures_by_frequency",
        or "raw_docs" for the resolved author(s). Never invent a structure
        name, id, or date from prior knowledge, even if it seems standard.
      - When asked for an author's "main"/"current" affiliation, prefer
        "primary_structures_by_frequency" (the structures that appear most
        often as PRIMARY across publications) over
        "all_linked_structures_by_frequency" (broader, includes institutional
        hierarchy noise — e.g. a lab's supervising universities that are not
        necessarily the author's own declared affiliation).
      - Present this as "based on how often this structure appears as a
        declared primary affiliation across N publications", not as a
        certified fact from HAL — HAL itself does not label anything as
        "the" current affiliation.
      - Do NOT infer an author's affiliation from a laboratory, university, or
        institution name appearing in a PUBLICATION TITLE or its content (e.g.
        a corpus name, a case study institution mentioned in the title). A
        structure name in a title is NOT evidence of the author's own
        affiliation. Only use structures found in this tool's dedicated
        affiliation fields, never from publication title/abstract text.
      - Do not label anything as an "implicit affiliation" or "mention
        implicite" — affiliation is either present in the data above or
        unknown; there is no in-between category to report.
      - If "authors_found" contains more than one homonym, ask the user to
        confirm which one they mean, or clearly present affiliations grouped
        by person — never merge two different people's affiliations together.
      - If num_found is 0 for the author search, or 0 for the affiliations,
        say so explicitly instead of guessing.
      - If an author has no usable hal_id, this is reported as an explicit
        error entry for that author — it is NOT the same as "no affiliations
        found", and must not be presented as such.
      - If has_more is true (for either step), mention that results were
        truncated and more may exist — do not present the list as exhaustive.
      - If affiliations_by_author for a given hal_id contains an "error" key,
        you MUST report that error to the user as-is (technical failure,
        affiliations unavailable). You must NOT compensate by inferring or
        guessing affiliations yourself from publication titles, abstracts,
        author names, or general knowledge about the field. A tool failure
        is not license to fall back on your own reasoning about what the
        affiliation "probably" is — say the data could not be retrieved and
        stop there.

    Parameters:
        nom_auteur: author name to search for (e.g. "Jean Dupont")
        rows: max number of affiliation records to retrieve per author (default: 100)

    Returns:
        authors_found: list of resolved authors, each with the fields
            {name, hal_id, docid, statut_validation}
            (these are the ONLY field names produced by author search — do
            not invent alternatives such as "id_hal" or "nom_complet")
        homonyms_warning: present if more than one author matched the name
        affiliations_by_author: dict mapping hal_id -> {
            num_found, total_returned, has_more, raw_docs, raw_fields_sample,
            primary_structures_by_frequency, all_linked_structures_by_frequency
        }, OR mapping a placeholder key -> {"error": ...} for any author that
        could not be processed (e.g. missing hal_id, or a failed API call).
        query_url_author_search: URL used to resolve the author name
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