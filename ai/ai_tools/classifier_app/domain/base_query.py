from pydantic import BaseModel

class Query(BaseModel):
    text : str
    
class QueryResult(BaseModel):
    query : str
    label : str