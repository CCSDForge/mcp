from core.mcp import mcp
from hal_api.search_lab_publications import search_lab_publications
import hashlib
import sys


def _format_report(pagination_log: list[str], counter: dict, top_n: int = 30) -> str:
    lines = []
    lines.extend(pagination_log)
    lines.append("")
    lines.append(f"Top {top_n} mots-clés")
    lines.append("")

    top_items = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    for keyword, count in top_items:
        lines.append(f"{count:4d}  {keyword}")

    body = "\n".join(lines)

    # Auto-vérification intégrée AU CONTENU (pas juste dans la docstring) :
    # ça donne au modèle un moyen de se corriger lui-même s'il a paraphrasé.
    total_occurrences = sum(c for _, c in top_items)
    n_lines = len(top_items)
    check = (
        f"[CHECK] {n_lines} mots-clés listés, "
        f"somme des occurrences affichées = {total_occurrences}"
    )

    banner_top = (
        "### DÉBUT RAPPORT HAL — NE PAS MODIFIER, NE PAS RECALCULER ###"
    )
    banner_bottom = (
        "### FIN RAPPORT HAL — recopier tel quel dans un bloc de code, "
        "chiffres inclus, sans reformuler ###"
    )

    return f"{banner_top}\n\n{body}\n\n{check}\n\n{banner_bottom}"


@mcp.tool()
async def hal_get_lab_publications(structure_id: str, year: int | None = None) -> dict:
    """
    Compte les mots-clés des publications d'une structure HAL (id numérique
    structId_i), pour une année précise si fournie, sinon toutes années
    confondues.

    PRÉREQUIS : nécessite un structure_id NUMÉRIQUE déjà connu. Si tu n'as
    qu'un NOM de structure, appelle D'ABORD le tool search structure pour
    résoudre le nom en id.

    Args:
        structure_id: identifiant HAL numérique de la structure (structId_i).
        year: année exacte (ex: 2026), ou None pour toutes les années.

    Returns:
        raw_text_report (str): rapport déjà entièrement formaté, avec
            bannières de début/fin et une ligne [CHECK] d'auto-vérification.
            C'est la SEULE source de vérité pour les chiffres.
        control_hash, num_found, total_returned, query_url.

    RÈGLE STRICTE :
      1. Affiche "raw_text_report" tel quel dans un bloc de code, du début
         "### DÉBUT RAPPORT" à la fin "### FIN RAPPORT" inclus.
      2. N'utilise JAMAIS d'autre champ que raw_text_report pour produire des
         chiffres ou une liste de mots-clés dans ta réponse.
      3. Ne recalcule rien, ne trie pas différemment, n'arrondis pas.
      4. Affiche ensuite "Vérification : {control_hash}".
      5. Si la ligne [CHECK] à l'intérieur du rapport ne correspond pas à ce
         que tu es sur le point d'écrire, arrête-toi et recopie le rapport
         intégralement au lieu de le reformuler.
    """
    result = await search_lab_publications(structure_id=structure_id, year=year)

    if "error" in result:
        return {"error": result["error"], "query_url": result.get("query_url")}

    raw_text_report = _format_report(result["pagination_log"], result["counter"])
    control_hash = hashlib.sha256(raw_text_report.encode("utf-8")).hexdigest()[:8]

    print("=" * 60, file=sys.stderr)
    print(f"DEBUG hal_get_lab_publications -- control_hash: {control_hash}", file=sys.stderr)
    print(raw_text_report, file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    return {
        "raw_text_report": raw_text_report,
        "control_hash": control_hash,
        "num_found": result["num_found"],
        "total_returned": result["total_returned"],
        "query_url": result["query_url"],
        # "counter" volontairement retiré du retour public : c'est cette
        # présence côté LLM qui l'invitait à recompter/reformuler.
    }