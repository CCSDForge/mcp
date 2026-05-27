import aiohttp
from typing import Optional
from typing import List, Union, Dict

BASE_URL = "https://api.archives-ouvertes.fr/search/"

BASE_AUTHOR_URL = f"{BASE_URL}/ref/author/"

"""
hal_api.py
----------
Couche d'accès à l'API HAL (archives-ouvertes.fr).
Toutes les fonctions sont async et utilisent aiohttp.
"""

async def search_authors(query: str, rows: int = 10) -> list[dict]:
    """
    Recherche des auteurs dans le référentiel HAL.

    Args:
        query: nom ou fragment de nom de l'auteur.
        rows:  nombre maximum de résultats.

    Returns:
        Liste de dicts avec les clés : name, hal_id, docid, structure
    """
    params = {
        "q": f"text:{query}",
        "wt": "json",
        "fl": "label_s,idHal_s,docid,structure_s",
        "rows": rows,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_AUTHOR_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    docs = data.get("response", {}).get("docs", [])
    return [
        {
            "name": d.get("label_s"),
            "hal_id": d.get("idHal_s"),
            "docid": d.get("docid"),
            "structure": d.get("structure_s"),
        }
        for d in docs
    ]

