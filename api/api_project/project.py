from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models import project as models
from models.base_models import EAPIResponseCode
from commons.service_logger.logger_factory_service import SrvLoggerFactory
from config import ConfigClass
import requests

router = APIRouter()
_API_NAMESPACE = "api_project"


@cbv(router)
class FileCheck:

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get('/{project_code}/file/exist',
                response_model=models.CheckFileResponse,
                tags=["File Check"],
                summary="Check file exists")
    async def get(self, project_code, zone, file_relative_path):
        """
        Check if file exists in given project/folder
        """
        self._logger.info("api_project_get".center(80, '-'))
        api_response = models.CheckFileResponse()
        url = ConfigClass.NEO4J_SERVICE_V2 + "nodes/query"
        self._logger.info(f"Received info: project_code: {project_code}, zone: {zone}, "
                          f"file_relative_path: {file_relative_path}")
        zone = {"vrecore": "VRECore", "greenroom": "Greenroom"}.get(zone.lower(), '')
        if not zone:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid zone"
            return api_response.json_response()
        data = {'query': {
            "display_path": file_relative_path,
            "project_code": project_code,
            "labels": ['File', zone]
        }
        }
        self._logger.info(f"POST payload: {data}")
        self._logger.info(f"POST url: {url}")
        try:
            res = requests.post(url=url, json=data)
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
        elif not res:
            code = EAPIResponseCode.not_found
            error_msg = 'File not found'
            result = res
        else:
            code = EAPIResponseCode.internal_error
            result = res.json
            error_msg = 'Internal Error'
        api_response.code = code
        api_response.result = result
        api_response.error_msg = error_msg
        return api_response.json_response()


