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

import httpx
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from logger import LoggerFactory

from config import ConfigClass
from models import project as models
from models.base_models import EAPIResponseCode

router = APIRouter()
_API_NAMESPACE = "api_project"


@cbv(router)
class FileCheck:

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.get('/{project_code}/file/exist',
                response_model=models.CheckFileResponse,
                tags=["File Check"],
                summary="Check file exists")
    def get(self, project_code, zone, file_relative_path):
        """
        Check if file exists in given project/folder
        """
        self._logger.info("api_project_get".center(80, '-'))
        api_response = models.CheckFileResponse()
        url = ConfigClass.NEO4J_SERVICE_V2 + "nodes/query"
        self._logger.info(f"Received info: project_code: {project_code}, zone: {zone}, "
                          f"file_relative_path: {file_relative_path}")
        zone = {"core": "Core", "greenroom": "Greenroom"}.get(zone.lower(), '')
        if not zone:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid zone"
            return api_response.json_response()
        data = {'query': {
            "display_path": file_relative_path,
            "project_code": project_code,
            "labels": ['File', zone],
            "archived": False
        }
        }
        self._logger.info(f"POST payload: {data}")
        self._logger.info(f"POST url: {url}")
        try:
            with httpx.Client() as client:
                res = client.post(url=url, json=data)
            self._logger.info(f"POST response: {res.text}")
            res = res.json().get('result')
            self._logger.info(f"POST result: {res}")
        except Exception as e:
            self._logger.error(f"POST ERROR: {str(e)}")
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = str(e)
            return api_response.json_response()
        if res:
            code = EAPIResponseCode.success
            result = res
            error_msg = ''
        else:
            code = EAPIResponseCode.not_found
            error_msg = 'File not found'
            result = res
        api_response.code = code
        api_response.result = result
        api_response.error_msg = error_msg
        return api_response.json_response()
