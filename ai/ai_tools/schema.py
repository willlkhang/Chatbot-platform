from pydantic import BaseModel

# Used for /create
class MaterialSchema(BaseModel):
    topic: int
    content: str

# Used for /get (Expects exactly {"topic": 1})
class GetMaterialSchema(BaseModel):
    topic: int

# Used for /classify (Expects exactly {"content": "some text"})
class ClassifySchema(BaseModel):
    content: str