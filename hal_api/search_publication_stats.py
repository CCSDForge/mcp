import aiohttp

BASE_URL = "https://api.archives-ouvertes.fr/search/"

async def search_publication_stats(
    struct_id: int,
    start_year: int,
    end_year: int,
    rows: int = 10000
):
    params = {
        "q": "*:*",
        "fq": (
            f"structId_i:{struct_id} "
            f"AND producedDateY_i:[{start_year} TO {end_year}]"
        ),
        "fl": "producedDateY_i,docType_s",
        "rows": rows
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as resp:
            data = await resp.json()

            docs = data.get("response", {}).get("docs", [])

            return [
                {
                    "year": d.get("producedDateY_i"),
                    "type": d.get("docType_s")
                }
                for d in docs
            ]
