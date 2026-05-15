"""Pydantic models for DB-related API requests and responses."""

from pydantic import BaseModel


class AddResourceRequest(BaseModel):
    topic: str
    resource: str


class GetResourceResult(BaseModel):
    resources: list

