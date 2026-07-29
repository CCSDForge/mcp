import aiohttp

BASE_AUTHOR_URL = "https://api.archives-ouvertes.fr/ref/author/"


async def search_authors(query: str, rows: int = 10) -> dict:
    """
    Recherche des auteurs dans le référentiel HAL (/ref/author).

    Args:
        query: nom ou fragment de nom de l'auteur.
        rows:  nombre maximum de résultats.

    Returns:
        dict avec num_found, total_returned, has_more, authors, query_url
        ou {"error": ..., "query_url": ...} en cas d'échec.

        Chaque élément de "authors" a la forme :
        {"name": ..., "hal_id": ..., "docid": ..., "statut_validation": ...}
    """
    params = {
        "q": f'text:"{query}"',
        "wt": "json",
        "fl": "label_s,idHal_s,docid,valid_s",
        "rows": rows,
    }

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(BASE_AUTHOR_URL, params=params) as resp:
                query_url = str(resp.url)
                if resp.status != 200:
                    return {
                        "error": f"L'API HAL a répondu avec le code {resp.status}",
                        "query_url": query_url,
                    }
                try:
                    data = await resp.json(content_type=None)
                except Exception as e:
                    return {
                        "error": f"Réponse HAL non-JSON ou invalide : {e}",
                        "query_url": query_url,
                    }
    except aiohttp.ClientError as e:
        return {"error": f"Erreur réseau lors de l'appel à l'API HAL : {e}", "query_url": None}
    except Exception as e:
        return {"error": f"Erreur inattendue lors de l'appel à l'API HAL : {e}", "query_url": None}

    response_block = data.get("response", {})
    docs = response_block.get("docs", [])
    num_found = response_block.get("numFound", len(docs))

    authors = [
        {
            "name": d.get("label_s"),
            "hal_id": d.get("idHal_s"),
            "docid": d.get("docid"),
            "statut_validation": d.get("valid_s"),
        }
        for d in docs
    ]

    return {
        "num_found": num_found,
        "total_returned": len(authors),
        "has_more": num_found > len(authors),
        "authors": authors,
        "query_url": query_url,
    }