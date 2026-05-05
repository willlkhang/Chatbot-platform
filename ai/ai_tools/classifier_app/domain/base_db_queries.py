from pydantic import BaseModel

class AddResourceRequest(BaseModel):
    topic : str
    resource : str

class GetResourceResult(BaseModel):
    resources : list

