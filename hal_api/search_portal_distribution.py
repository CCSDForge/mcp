import aiohttp
from typing import Optional
from typing import List, Union, Dict

BASE_URL = "https://api.archives-ouvertes.fr/search/"

BASE_SEARCH_URL = f"{BASE_URL}/search/"
 
def _build_struct_filter(struct_ids: List[int]) -> str:
    """
    Build HAL filter query for one or multiple structure IDs.
    """
    return " OR ".join([f"structId_i:{sid}" for sid in struct_ids])


async def search_portal_distribution(
    struct_ids: Union[int, List[int]],
    year: int,
    with_file: bool = False
) -> Dict[str, int]:
    """
    Query HAL API to get distribution of deposits by portal (instance_s).

    Parameters:
    - struct_ids: int or list[int]
    - year: int
    - with_file: bool → filter deposits with full-text file

    Returns:
    - dict {portal: count}
    """

    # normalisation
    if isinstance(struct_ids, int):
        struct_ids = [struct_ids]

    struct_filter = _build_struct_filter(struct_ids)

    fq = f"({struct_filter}) AND submittedDateY_i:{year}"

    if with_file:
        fq += " AND submitType_s:file"

    params = {
        "q": "*:*",
        "fq": fq,
        "facet": "true",
        "facet.field": "instance_s",
        "rows": 0
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    facets = (
        data.get("facet_counts", {})
            .get("facet_fields", {})
            .get("instance_s", [])
    )

    # transformation en dict
    return {
        facets[i]: facets[i + 1]
        for i in range(0, len(facets), 2)
    }
