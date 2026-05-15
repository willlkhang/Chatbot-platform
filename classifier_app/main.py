"""Entrypoint for the classifier FastAPI application.

This module wires together the FastAPI app, initializes a classifier
instance and a database helper, and mounts the routers defined in
`controllers`. Only comments and docstrings are added; runtime behavior
remains unchanged.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from classifiers import LinearSVC
from controllers import classify_routers, db_routers, home_router
from databases import SQLiteDB


app = FastAPI()

_cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# attach shared instances to the app state for use in route handlers
app.state.classifier = LinearSVC()
app.state.db = SQLiteDB()

# include API routers implemented in the controllers package
app.include_router(classify_routers)
app.include_router(db_routers)
app.include_router(home_router)


if __name__ == "__main__":
    host = os.environ.get("CLASSIFIER_HOST", "0.0.0.0")
    port = int(os.environ.get("CLASSIFIER_PORT", "8011"))
    reload = os.environ.get("CLASSIFIER_RELOAD", "true").lower() in ("1", "true", "yes")
    uvicorn.run("main:app", host=host, port=port, reload=reload)