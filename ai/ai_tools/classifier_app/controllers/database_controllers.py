from fastapi import APIRouter

router  = APIRouter()
    
@router.post("/add")
def add():
    ...
    
@router.get("/get_topic")
def get_topic():
    ...