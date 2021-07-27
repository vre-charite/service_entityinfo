from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models import attributes as models
from models.base_models import EAPIResponseCode
from resources.error_handler import catch_internal
from commons.service_logger.logger_factory_service import SrvLoggerFactory
from config import ConfigClass
import requests
import math
import time
from .utils import get_files_recursive, get_file_node_bygeid, get_folder_node_bygeid, is_valid_file, attach_attributes, has_valid_attributes

router = APIRouter()
_API_NAMESPACE = "file_attributes_restful"


@cbv(router)
class AttachAttributes:
    def __init__(self):
        self._logger = SrvLoggerFactory('api_attributes').get_logger()

    @router.post('/attach', summary="Attach attributes on file")
    @catch_internal(_API_NAMESPACE)
    async def post(self, data: models.AttachAttributesPOST):
        api_response = models.AttachPOSTResponse()
        self._logger.info(f"file data payload: {data}")

        manifest_id = data.manifest_id
        global_entity_id = data.global_entity_id
        attributes = data.attributes
        inherit = data.inherit
        project_role = data.project_role
        username = data.username

        # res = requests.get(ConfigClass.BFF_SERVICE + 'data/manifest/{}'.format(manifest_id))
        res = requests.get(ConfigClass.ENTITYINFO_SERVICE + f"manifest/{manifest_id}")
        manifest = None
        if res.status_code == 200:
            manifest_data = res.json()
            manifest = manifest_data['result']
            self._logger.info(f"file manifest: {manifest}")
        else:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "can not get manifest data with manifest_id: {}".format(
                manifest_id)
            self._logger.error(f"file manifest error: {res.text}")
            return api_response.json_response()

        sql_attributes = manifest['attributes']

        result_list = []

        valid, error_msg = has_valid_attributes(sql_attributes, attributes)
        if not valid:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = error_msg
            return api_response.json_response()

        for geid in global_entity_id:
            file_node = get_file_node_bygeid(geid)

            if not file_node:
                folder_node = get_folder_node_bygeid(geid)
                child_files = get_files_recursive(geid, [])
                if len(child_files) == 0:
                    continue

                for child_file in child_files:
                    # Make sure it's Greenroom file
                    if "manifest_id" in child_file:
                        result_list.append({
                            "name": child_file["name"],
                            "geid": child_file["global_entity_id"],
                            "operation_status": "TERMINATED",
                            "error_type": "attributes_duplicate"
                        })
                        continue

                    is_success = attach_attributes(
                        manifest, attributes, child_file, self._logger)
                    if is_success:
                        result_list.append({
                            "name": child_file["name"],
                            "geid": child_file["global_entity_id"],
                            "operation_status": "SUCCEED"
                        })
                    else:
                        result_list.append({
                            "name": child_file["name"],
                            "geid": child_file["global_entity_id"],
                            "operation_status": "TERMINATED",
                            "error_type": "internal_error"
                        })
            else:
                if "manifest_id" in file_node:
                    result_list.append({
                        "name": file_node["name"],
                        "geid": file_node["global_entity_id"],
                        "operation_status": "TERMINATED",
                        "error_type": "attributes_duplicate"
                    })
                    continue

                is_success = attach_attributes(
                    manifest, attributes, file_node, self._logger)

                if is_success:
                    result_list.append({
                        "name": file_node["name"],
                        "geid": file_node["global_entity_id"],
                        "operation_status": "SUCCEED"
                    })
                else:
                    result_list.append({
                        "name": file_node["name"],
                        "geid": file_node["global_entity_id"],
                        "operation_status": "TERMINATED",
                        "error_type": "internal_error"
                    })

        api_response.result = result_list
        api_response.code = EAPIResponseCode.success
        api_response.total = len(result_list)

        return api_response.json_response()