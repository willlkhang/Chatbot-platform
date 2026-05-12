"""API routes exposing the classifier and model metadata.

Provides a `/query` endpoint to classify text and return related
resources, and `/get_topics` to list available model topics.
"""

from fastapi import APIRouter, Request
from domain import Query, QueryResult, ModelTopics
from classifiers import BaseTopicClassifier
from databases import BaseDB

classify_routers = APIRouter()


@classify_routers.post("/query")
def query(query: Query, requests: Request):
    """Classify `query.text` and return suggestion resources."""

    classifier: BaseTopicClassifier = requests.app.state.classifier
    label = classifier.classify(query.text)

    db: BaseDB = requests.app.state.db
    resource = db.get_resources(topic=label)

    return QueryResult(query=query.text, label=label, resource=resource)


@classify_routers.get("/get_topics")
def get_topics(requests: Request):
    """Return the list of topics the model knows about."""

    model: BaseTopicClassifier = requests.app.state.classifier
    topics = model.get_topics()
    return ModelTopics(topics=topics)