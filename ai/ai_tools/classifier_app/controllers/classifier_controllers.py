from fastapi import APIRouter, Request
from domain import Query, QueryResult
from classifiers import BaseTopicClassifier
from databases import BaseDB

classify_routers = APIRouter()

@classify_routers.post("/query")
def query(query : Query, requests : Request):
    
    classifier : BaseTopicClassifier = requests.app.state.classifier
    label = classifier.classify(query.text)
    
    db : BaseDB = requests.app.state.db
    resource = db.get_resources(topic=label)
    
    return QueryResult(query=query.text, 
                       label=label,
                       resource=resource)