# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

from fastapi import APIRouter
from api.api_files import files, files_v2, meta, files_stats
from api.api_users import users
from api.api_project import project
from api.api_folders import folders
from api.api_workbench import workbench
from api.api_manifest import manifest_router
from api.api_attributes import file_attributes
from api.api_metrics import system_metrics

api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
api_router.include_router(folders.router, tags=["Folder Entity Restful"])
api_router.include_router(meta.router, prefix="/files", tags=["files"])
api_router.include_router(files_stats.router, tags=["file-statistics"])
api_router.include_router(workbench.router, tags=["workbench"])
api_router.include_router(manifest_router, tags=["manifest"])
api_router.include_router(file_attributes.router)
api_router.include_router(system_metrics.router, tags=["System-Metrics"])


api_router_v2 = APIRouter()
api_router_v2.include_router(files_v2.router, prefix="/files", tags=["files"])
