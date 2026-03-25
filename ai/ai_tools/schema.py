from pydantic import BaseModel

class MaterialSchema(BaseModel):
    
    topic: int
    content: str