from fastapi import APIRouter
from app.api.endpoints.openai import openai_module

openai_router = APIRouter()


openai_router.include_router(
    openai_module,
    prefix="",
    tags=["openai"],
    responses={404: {"description": "Not found"}},
)

