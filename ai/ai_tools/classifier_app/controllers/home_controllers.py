from fastapi import APIRouter
from fastapi.responses import RedirectResponse

home_router = APIRouter()

@home_router.get("/")
def root():
    return RedirectResponse(url="/docs")