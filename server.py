from core.mcp import mcp
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from auth_users import ALLOWED_USERS
import jwt
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

#MCP tools
import hal_tools.hal_get_portal_distribution_with_files
import hal_tools.hal_get_publication_stats_by_structure
import hal_tools.hal_search_author_publications
import hal_tools.hal_search_authors
import hal_tools.hal_get_lab_publications

app = mcp.streamable_http_app()
logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.environ.get("MCP_JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("MCP_JWT_SECRET non définie dans le fichier .env !")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Endpoints publics
        if request.url.path in ["/docs", "/openapi.json", "/health"]:
            return await call_next(request)

        # Lire le header Authorization
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
                content={"error": "Unauthorized"}
            )

        token = auth_header[7:]

        # Vérifier et décoder le JWT
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"error": "Token expiré, contactez l'administrateur"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"error": "Token invalide"}
            )

        if username not in ALLOWED_USERS:
            return JSONResponse(
                status_code=403,
                content={"error": "Accès refusé"}
            )

        # Stocker l'utilisateur dans la requête
        request.state.user = username

        # Log de connexion avec timestamp
        logging.info(
            f"MCP access - user={username} "
            f"path={request.url.path} "
            f"client={request.client.host if request.client else 'unknown'} "
            f"timestamp={datetime.now().isoformat()}"
        )
        return await call_next(request)

app.add_middleware(AuthMiddleware)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")