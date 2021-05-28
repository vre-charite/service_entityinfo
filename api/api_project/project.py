from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models import project as models
from models.project import http_query_node
from models.base_models import EAPIResponseCode
from config import ConfigClass
import requests

router = APIRouter()


@cbv(router)
class FileCheck:
    @router.get('/{project_code}/file/exist',
                response_model=models.CheckFileResponse,
                tags=["File Check"],
                summary="Check file exists")
    async def get(self, project_code, zone, type, file_relative_path):
        """
        Check if file exists in given project,
        if file in a particular folder, could use folder in type
        e.g. type_name='processed/straight_copy'
        """
        api_response = models.CheckFileResponse()
        url = ConfigClass.NEO4J_SERVICE_V2 + "nodes/query"
        data_type = type.split('/')[0]
        if 'raw' != data_type and 'processed' != data_type:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = f"Invalid type {data_type}"
            return api_response.json_response()
        if zone.lower() == 'greenroom':
            zone = 'Greenroom'
            full_path = ConfigClass.NFS_ROOT_PATH + f'/{project_code}/raw/{file_relative_path}'
        elif zone.lower() == 'vrecore':
            zone = 'VRECore'
            full_path = ConfigClass.VRE_ROOT_PATH + f'/{project_code}/{file_relative_path}'
        else:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid zone"
            return api_response.json_response()
        data = {'query': {
            "full_path": full_path,
            "labels": ['File', zone]
        }
        }
        try:
            res = requests.post(url=url, json=data)
            res = res.json().get('result')
        except Exception as e:
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


