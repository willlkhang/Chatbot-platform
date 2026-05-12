"""Entrypoint for the classifier FastAPI application.

This module wires together the FastAPI app, initializes a classifier
instance and a database helper, and mounts the routers defined in
`controllers`. Only comments and docstrings are added; runtime behavior
remains unchanged.
"""

import uvicorn
from fastapi import FastAPI
from classifiers import LinearSVC
from controllers import classify_routers, db_routers, home_router
from databases import SQLiteDB


app = FastAPI()

# attach shared instances to the app state for use in route handlers
app.state.classifier = LinearSVC()
app.state.db = SQLiteDB()

# include API routers implemented in the controllers package
app.include_router(classify_routers)
app.include_router(db_routers)
app.include_router(home_router)


if __name__ == "__main__":
    # start development server; keep reload for convenience
    uvicorn.run("main:app", host="localhost", port=8011, reload=True)