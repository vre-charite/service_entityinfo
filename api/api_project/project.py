from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models import project as models
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
    async def get(self, project_code, zone, type, filename):
        """
        Check if file exists in given project,
        if file in a particular folder, could use folder in type
        e.g. type_name='processed/straight_copy'
        """
        api_response = models.CheckFileResponse()
        url = ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/query"
        data_type = type.split('/')[0]
        if 'raw' != data_type and 'processed' != data_type:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = f"Invalid type {data_type}"
            return api_response.json_response()
        elif data_type.lower() == 'processed':
            label_type = 'Processed'
        else:
            label_type = 'Raw'
        if zone.lower() == 'greenroom':
            zone = 'Greenroom'
            path = f"/data/vre-storage/{project_code}/{type}"
        elif zone.lower() == 'vrecore':
            zone = 'VRECore'
            path = f"/vre-data/{project_code}/raw"
        else:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid zone"
            return api_response.json_response()
        labels = ['File', label_type, zone]
        data = {'end_params': {'name': filename,
                               'path': path},
                'end_label': labels,
                'start_label': 'Dataset',
                'start_params': {'code': project_code}}
        try:
            res = requests.post(url=url, json=data)
            res = res.json()
        except Exception as e:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = str(e)
            return api_response.json_response()
        if len(res) == 1:
            code = EAPIResponseCode.success
            result = res[0]['end_node']
        elif len(res) == 0:
            code = EAPIResponseCode.not_found
            result = 'File not found'
        else:
            code = EAPIResponseCode.internal_error
            result = res
        api_response.code = code
        api_response.result = result
        return api_response.json_response()
