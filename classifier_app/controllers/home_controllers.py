"""Simple home route that redirects to the API docs.

This module defines a small `home_router` exposing a root endpoint
that redirects to the automatically generated Swagger UI documentation
at `/docs`.
"""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

home_router = APIRouter()


@home_router.get("/")
def root():
    # Redirect to FastAPI's automatically provided docs UI
    return RedirectResponse(url="/docs")