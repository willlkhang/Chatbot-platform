"""Pydantic models used by the classifier API routes."""

from pydantic import BaseModel


class Query(BaseModel):
    text: str


class QueryResult(BaseModel):
    query: str
    label: str
    resource: list


class ModelTopics(BaseModel):
    topics: list