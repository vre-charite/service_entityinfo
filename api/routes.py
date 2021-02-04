from fastapi import APIRouter
from api.api_files import files

api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
