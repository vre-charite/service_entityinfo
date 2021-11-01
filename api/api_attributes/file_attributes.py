import requests

from fastapi_sqlalchemy import db
from fastapi_utils.cbv import cbv
from fastapi import APIRouter
from commons.service_logger.logger_factory_service import SrvLoggerFactory
from config import ConfigClass
from models import attributes as models
from models import manifest
from models.base_models import APIResponse, EAPIResponseCode
from models.manifest_sql import DataAttributeModel
from resources.error_handler import catch_internal
from .utils import get_files_recursive, get_file_node_bygeid, get_folder_node_bygeid, attach_attributes, \
    has_valid_attributes

router = APIRouter()
_API_NAMESPACE = "file_attributes_restful"
_logger = SrvLoggerFactory("file_attributes").get_logger()


@cbv(router)
class AttachAttributes:
    def __init__(self):
        self._logger = SrvLoggerFactory('api_attributes').get_logger()

    @router.post('/files/attributes/attach', summary="Attach attributes on file", tags=['files'])
    @catch_internal(_API_NAMESPACE)
    async def post(self, data: models.AttachAttributesPOST):
        api_response = models.AttachPOSTResponse()
        self._logger.info(f"file data payload: {data}")

        manifest_id = data.manifest_id
        global_entity_id = data.global_entity_id
        attributes = data.attributes

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


@cbv(router)
class RestfulAttributes:
    @router.post('/attributes', response_model=manifest.POSTAttributesResponse, summary="Bulk create attributes", tags=['attributes'])
    async def post(self, data: manifest.POSTAttributesRequest):
        api_response = APIResponse()
        attributes = data.attributes
        for item in attributes:
            required_fields = ["manifest_id", "name", "type", "value", "optional", "project_code"]
            model_data = {}
            for field in required_fields:
                if not field in item:
                    api_response.code = EAPIResponseCode.bad_request
                    api_response.result = f"Missing required field {field}"
                    _logger.error(api_response.result)
                    return api_response.json_response()
                model_data[field] = item[field]

            # check if connect to any files
            if not model_data["optional"]:
                response = requests.post(ConfigClass.NEO4J_SERVICE + "nodes/File/query/count", json={"manifest_id": model_data["manifest_id"]})
                if response.json()["count"] > 0:
                    api_response.code = EAPIResponseCode.forbidden
                    api_response.result = "Can't add required attributes to manifest attached to files"
                    _logger.error(api_response.result)
                    return api_response.json_response()
            attribute = DataAttributeModel(**model_data)
            db.session.add(attribute)
            db.session.commit()
            db.session.refresh(attribute)
        api_response.result = "Success"
        return api_response.json_response()


@cbv(router)
class RestfulAttribute:
    @router.put('/attribute/{attribute_id}', response_model=manifest.POSTAttributesResponse, summary="Update an attribute", tags=['attributes'])
    async def put(self, attribute_id, data: manifest.PUTAttributeRequest):
        my_res = APIResponse()
        attribute = db.session.query(DataAttributeModel).get(attribute_id)
        if not attribute:
            my_res.code = EAPIResponseCode.not_found
            my_res.error_msg = 'Attribute not found'
            _logger.error(my_res.error_msg)
            return my_res.json_response()

        if hasattr(data, "type") and data.type:
            try:
                attribute.type = getattr(manifest.TypeEnum, data.type)
            except AttributeError:
                my_res.code = EAPIResponseCode.bad_request
                my_res.result = "Invalid type"
                _logger.error(my_res.result)
                return my_res.json_response()
        update_fields = ["name", "attribute", "value", "optional", "project_code"]
        for field in update_fields:
            if hasattr(data, field):
                setattr(attribute, field, getattr(data, field))
        db.session.add(attribute)
        db.session.commit()
        db.session.refresh(attribute)
        my_res.result = attribute.to_dict()
        return my_res.json_response()

    @router.delete('/attribute/{attribute_id}', response_model=manifest.DELETEAttributeResponse, summary="Delete an attribute", tags=['attributes'])
    def delete(self, attribute_id):
        """
        Delete an attribute
        """
        my_res = APIResponse()
        attribute = db.session.query(DataAttributeModel).get(attribute_id)
        if not attribute:
            my_res.code = EAPIResponseCode.not_found
            my_res.error_msg = 'Attribute not found'
            _logger.error(my_res.error_msg)
            return my_res.json_response()

        db.session.delete(attribute)
        db.session.commit()
        my_res.result = "Success"
        return my_res.json_response()

