# api.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from mcp.server.sse import SseServerTransport
from core.mcp import mcp

# Import des tools pour les enregistrer auprès de mcp
import hal_tools.hal_search_authors
import hal_tools.hal_search_author_publications
import hal_tools.hal_get_publication_stats_by_structure
import hal_tools.hal_get_portal_distribution_with_files

# Import des fonctions HAL pour les endpoints REST
from hal_api.search_portal_distribution import search_portal_distribution
from hal_api.search_publication_stats import search_publication_stats
from hal_api.search_author_publications import search_author_publications
from hal_api.search_authors import search_authors

app = FastAPI(title="HAL MCP HTTP API")

# ── Transport MCP SSE ────────────────────────────────────────────────────────

sse = SseServerTransport("/mcp/messages")

@app.get("/mcp/sse")
async def sse_endpoint(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())

@app.post("/mcp/messages")
async def messages_endpoint(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

# ── Modèles ──────────────────────────────────────────────────────────────────

class PortalDistributionParams(BaseModel):
    struct_ids: int | list[int]
    year: int
    top_n: int = 20

class PublicationStatsParams(BaseModel):
    struct_id: int
    start_year: int
    end_year: int

class AuthorPublicationsParams(BaseModel):
    author_name: str
    start_year: int | None = None
    end_year: int | None = None
    rows: int = 50

class SearchAuthorsParams(BaseModel):
    query: str
    rows: int = 10


# ── Endpoints REST ───────────────────────────────────────────────────────────

@app.post("/tools/portal_distribution")
async def portal_distribution(params: PortalDistributionParams):
    try:
        import asyncio
        struct_ids = [params.struct_ids] if isinstance(params.struct_ids, int) else params.struct_ids
        total, with_file = await asyncio.gather(
            search_portal_distribution(struct_ids, params.year, False),
            search_portal_distribution(struct_ids, params.year, True),
        )
        results = []
        for portal, total_count in total.items():
            file_count = with_file.get(portal, 0)
            results.append({
                "portal": portal,
                "total": total_count,
                "with_file": file_count,
                "without_file": total_count - file_count,
                "file_ratio": round(file_count / total_count, 3) if total_count > 0 else 0,
            })
        results = sorted(results, key=lambda x: x["total"], reverse=True)[:params.top_n]
        return {"structure_ids": struct_ids, "year": params.year, "portals": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/publication_stats")
async def publication_stats(params: PublicationStatsParams):
    try:
        data = await search_publication_stats(
            struct_id=params.struct_id,
            start_year=params.start_year,
            end_year=params.end_year,
        )
        stats = {}
        for item in data:
            year = item["year"]
            ptype = item["type"] or "UNKNOWN"
            stats.setdefault(year, {}).setdefault(ptype, 0)
            stats[year][ptype] += 1
        return {
            "structure_id": params.struct_id,
            "period": f"{params.start_year}-{params.end_year}",
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/author_publications")
async def author_publications(params: AuthorPublicationsParams):
    try:
        publications = await search_author_publications(
            params.author_name,
            start_year=params.start_year,
            end_year=params.end_year,
            rows=params.rows,
        )
        with_abstract = [
            p for p in publications
            if p.get("abstract") and p["abstract"] != "Pas de résumé disponible"
        ]
        return {
            "total": len(publications),
            "with_abstract": len(with_abstract),
            "without_abstract": len(publications) - len(with_abstract),
            "publications": publications,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/search_authors")
async def search_authors_endpoint(params: SearchAuthorsParams):
    try:
        authors = await search_authors(params.query, rows=params.rows)
        return {"total": len(authors), "authors": authors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
