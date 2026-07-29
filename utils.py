from collections import defaultdict


def aggregate_by_year_and_type(publications):
    """
    Transform list of publications into:
    { year: { type: count } }
    """

    stats = defaultdict(lambda: defaultdict(int))

    for pub in publications:
        year = pub.get("year")
        ptype = pub.get("type") or "UNKNOWN"

        if not year:
            continue

        stats[year][ptype] += 1

    return stats


def aggregate_publications_by_year_and_doctype(publications):
    """
    Transform list of HAL publications into:
    { year: { doc_type: count } }

    Attend les clés "publication_year" et "doc_type" dans chaque publication
    (format renvoyé par les fonctions de hal_api/*.py : recherche ANR,
    recherche par structure, etc.)
    """
    stats = defaultdict(lambda: defaultdict(int))
    for pub in publications:
        year = pub.get("publication_year")
        ptype = pub.get("doc_type") or "UNKNOWN"
        if not year:
            continue
        stats[year][ptype] += 1
    return {year: dict(types) for year, types in stats.items()}


def format_keyword_report(pagination_log, keywords, top_n=30):
    lines = list(pagination_log)
    lines.append("")
    lines.append(f"Top {top_n} mots-clés :")

    for kw, count in list(keywords.items())[:top_n]:
        lines.append(f"{kw} : {count}")

    return "\n".join(lines)