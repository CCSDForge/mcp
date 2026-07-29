from core.mcp import mcp
from hal_api.search_lab_publications import search_lab_publications
import hashlib


def _format_report(pagination_log: list[str], counter: dict, top_n: int = 30) -> str:
    lines = list(pagination_log)
    lines.append("")
    lines.append(f"Top {top_n} mots-clés")
    lines.append("")
    top_items = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    for keyword, count in top_items:
        lines.append(f"{count:4d}  {keyword}")
    return "\n".join(lines)


@mcp.tool()
async def hal_get_lab_publications(structure_id: str, year: int | None = None) -> dict:
    """
    Compte les mots-clés des publications d'une structure HAL (id numérique
    structId_i), pour une année précise si fournie, sinon toutes années
    confondues.

    PRÉREQUIS : nécessite un structure_id NUMÉRIQUE déjà connu. Si tu n'as
    qu'un NOM de structure (ex: "Université Claude Bernard Lyon 1", "IP
    Paris"), appelle D'ABORD le tool search structure pour résoudre le nom en
    id, puis appelle cet outil avec l'id obtenu -- ne devine jamais un
    structure_id à partir d'un nom ou de connaissances générales.

    Args:
        structure_id: identifiant HAL numérique de la structure (structId_i).
        year: année exacte (ex: 2026), ou None pour toutes les années.

    Returns:
        raw_text_report (str): rapport texte déjà formaté (progression de
            récupération + top 30 mots-clés avec leurs comptages exacts).
        num_found, total_returned, query_url.

    RÈGLE STRICTE : quand l'utilisateur demande les mots-clés/thématiques,
    réponds en recopiant "raw_text_report" MOT POUR MOT dans un bloc de
    code, sans changer un seul chiffre ni un seul mot-clé, sans renommer,
    sans fusionner, sans arrondir, sans en inventer. Ne reformule pas ce
    contenu -- copie-le tel quel. Affiche aussi "control_hash" juste après
    le bloc de code (ex: "Vérification : abc12345"), pour que l'utilisateur
    puisse comparer ce code à celui affiché dans les logs du serveur et
    détecter immédiatement toute divergence.
    """
    result = await search_lab_publications(structure_id=structure_id, year=year)

    if "error" in result:
        return {"error": result["error"], "query_url": result.get("query_url")}

    raw_text_report = _format_report(result["pagination_log"], result["counter"])
    control_hash = hashlib.sha256(raw_text_report.encode("utf-8")).hexdigest()[:8]

    # DEBUG TEMPORAIRE : imprime dans les logs du serveur MCP (stderr), pour
    # vérifier indépendamment de l'interface de chat ce que le serveur
    # renvoie VRAIMENT. À retirer une fois le diagnostic terminé.
    import sys
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
    }