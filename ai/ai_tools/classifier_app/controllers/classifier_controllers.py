from fastapi import APIRouter, Request
from domain import Query, QueryResult

classify_routers = APIRouter()

@classify_routers.post("/classify")
def classify(query : Query, requests : Request):
    
    classifier = requests.app.state.classifier
    label = classifier.classify(query.text)
    
    return QueryResult(query=query.text, label=label)