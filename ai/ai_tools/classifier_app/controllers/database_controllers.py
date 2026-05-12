"""Database-related API routes for managing resource links."""

from fastapi import APIRouter, Request
from domain import AddResourceRequest, GetResourceResult
from databases import BaseDB

db_routers = APIRouter()


@db_routers.post("/add_resources")
def add_resources(add: AddResourceRequest, request: Request):
    """Add a resource entry to the backend database.

    The database instance is stored on `app.state.db` by the main
    application bootstrap.
    """

    db: BaseDB = request.app.state.db
    db.add_resources(topic=add.topic, resource=add.resource)


@db_routers.get("/get_resources")
def get_resources(topic: str, request: Request):
    """Return resources for the provided topic as `GetResourceResult`."""

    db: BaseDB = request.app.state.db
    results = db.get_resources(topic=topic)

    return GetResourceResult(resources=results)
    