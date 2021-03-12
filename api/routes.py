from fastapi import APIRouter
from api.api_files import files
from api.api_users import users
from api.api_project import project

api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
