from fastapi import APIRouter
from api.api_files import files, files_v2, meta, files_stats
from api.api_users import users
from api.api_project import project
from api.api_folders import folders
from api.api_workbench import workbench 
from api.api_manifest import manifest 
from api.api_attributes import file_attributes


api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
# api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
api_router.include_router(folders.router, tags=["Folder Entity Restful"])
api_router.include_router(meta.router, prefix="/files", tags=["files"])
api_router.include_router(files_stats.router, tags=["file-statistics"])
api_router.include_router(workbench.router, tags=["workbench"])
api_router.include_router(manifest.router, tags=["manifest"])
api_router.include_router(file_attributes.router)


api_router_v2 = APIRouter()
api_router_v2.include_router(files_v2.router, prefix="/files", tags=["files"])
