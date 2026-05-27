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
