from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from fastapi_sqlalchemy import db
from models import manifest
from models.manifest_sql import DataManifestModel , DataAttributeModel
from models.base_models import APIResponse, EAPIResponseCode
from datetime import datetime
import requests
from config import ConfigClass
from .utils import is_greenroom, get_file_node_bygeid, get_trashfile_node_bygeid, \
        has_valid_attributes, check_attributes, get_folder_node_bygeid
from commons.service_logger.logger_factory_service import SrvLoggerFactory
import time
import re

router = APIRouter()
_logger = SrvLoggerFactory("api_manifest").get_logger()


@cbv(router)
class RestfulManifests:
    @router.get('/manifests', response_model=manifest.GETManifestsResponse, summary="List manifests by project_code")
    async def get(self, project_code: str):
        """
        List manifests by project_code
        """
        my_res = APIResponse()
        manifests = db.session.query(DataManifestModel).filter_by(project_code=project_code)
        results = []
        for manifest in manifests:
        #for manifest in manifests.items:
            result = manifest.to_dict()
            result["attributes"] = []
            attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest.id).\
                    order_by(DataAttributeModel.id.asc())
            for atr in attributes:
                result["attributes"].append(atr.to_dict())
            results.append(result)
        #my_res.set_page(manifests.page)
        #my_res.set_num_of_pages(manifests.pages)
        my_res.total = len(results)
        my_res.result = results
        return my_res.json_response()

    @router.post('/manifests', response_model=manifest.POSTManifestsResponse, summary="Create a data manifest")
    async def post(self, data: manifest.POSTManifestsRequest):
        api_response = APIResponse()

        manifests = db.session.query(DataManifestModel).filter_by(project_code=data.project_code)
        if manifests.count() > 9:
            api_response.code = EAPIResponseCode.forbidden
            api_response.result = "Manifest limit reached"
            _logger.error(api_response.result)
            return api_response.json_response()

        for item in manifests:
            result = item.to_dict()
            if data.name == result["name"]:
                api_response.code = EAPIResponseCode.bad_request
                api_response.result = "duplicate manifest name"
                _logger.error(api_response.result)
                return api_response.json_response()
        model_data = {
            "name": data.name,
            "project_code": data.project_code,
        }
        manifest = DataManifestModel(**model_data)
        db.session.add(manifest)
        db.session.commit()
        db.session.refresh(manifest)

        api_response.result = manifest.to_dict()
        return api_response.json_response()

@cbv(router)
class RestfulManifest:
    @router.get('/manifest/{manifest_id}', response_model=manifest.GETManifestResponse, summary="Get a single manifest")
    async def get(self, manifest_id):
        """
        Get a data manifest and list attributes
        """
        my_res = APIResponse()
        manifest = db.session.query(DataManifestModel).get(manifest_id)
        if not manifest:
            my_res.code = EAPIResponseCode.not_found
            my_res.error_msg = 'Manifest not found'
            _logger.error(my_res.error_msg)
        else:
            result = manifest.to_dict()
            result["attributes"] = []
            attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest_id).\
                    order_by(DataAttributeModel.id.asc())
            for atr in attributes:
                result["attributes"].append(atr.to_dict())
            my_res.result = result
        return my_res.json_response()

    @router.put('/manifest/{manifest_id}', response_model=manifest.PUTManifestResponse, summary="update a single manifest")
    def put(self, manifest_id, data: manifest.PUTManifestRequest):
        my_res = APIResponse()
        manifest = db.session.query(DataManifestModel).get(manifest_id)
        if not manifest:
            my_res.code = EAPIResponseCode.not_found
            my_res.error_msg = 'Manifest not found'
            _logger.error(my_res.error_msg)
            return my_res.json_response()

        if hasattr(data, "type"):
            try:
                manifest.type = getattr(manifest.TypeEnum, data.type)
            except AttributeError:
                my_res.code = EAPIResponseCode.bad_request
                my_res.result = "Invalid type"
                _logger.error(my_res.result)
                return my_res.json_response()
        update_fields = ["name", "project_code"]
        for field in update_fields:
            if hasattr(data, field):
                setattr(manifest, field, getattr(data, field))
        db.session.add(manifest)
        db.session.commit()
        db.session.refresh(manifest)
        my_res.result = manifest.to_dict()
        return my_res.json_response()

    @router.delete('/manifest/{manifest_id}', response_model=manifest.DELETEManifestResponse, summary="delete a single manifest")
    def delete(self, manifest_id):
        my_res = APIResponse()
        manifest = db.session.query(DataManifestModel).get(manifest_id)
        if not manifest:
            my_res.code = EAPIResponseCode.not_found
            my_res.error_msg = 'Manifest not found'
            _logger.error(my_res.error_msg)
            return my_res.json_response()

        # check if connect to any files
        response = requests.post(ConfigClass.NEO4J_SERVICE + "nodes/File/query/count", json={"manifest_id": int(manifest_id)})
        if response.json()["count"] > 0:
            my_res.code = EAPIResponseCode.forbidden
            my_res.result = "Can't delete manifest attached to files"
            _logger.error(my_res.result)
            return my_res.json_response()

        attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest.id)
        for atr in attributes:
            db.session.delete(atr)
        db.session.commit()
        db.session.delete(manifest)
        db.session.commit()
        my_res.result = "success"
        return my_res.json_response()


@cbv(router)
class ImportManifest:
    @router.post('/manifest/file/import', response_model=manifest.POSTImportResponse, summary="Import a data manifest")
    def post(self, data: manifest.POSTImportRequest):
        api_response = APIResponse()
        # limit check
        manifests = db.session.query(DataManifestModel).filter_by(project_code=data.project_code)
        if manifests.count() > 9:
            api_response.code = EAPIResponseCode.forbidden
            api_response.result = "Manifest limit reached"
            _logger.error(api_response.result)
            return api_response.json_response()

        for manifest in manifests:
            result = manifest.to_dict()
            if data.name == result["name"]:
                api_response.code = EAPIResponseCode.bad_request
                api_response.result = "duplicate manifest name"
                _logger.error(api_response.result)
                return api_response.json_response()

        manifest_data = {
            "name": data.name,
            "project_code": data.project_code
        }
        # Create manifest in psql
        manifest = DataManifestModel(**manifest_data)
        db.session.add(manifest)
        db.session.commit()
        db.session.refresh(manifest)

        attributes = data.attributes
        attr_data = {}
        mutli_requirement = re.compile("^[a-zA-z0-9-_!%&/()=?*+#.;,]{1,32}$")
        for attr in attributes:
            if attr["name"] in attr_data:
                api_response.code = EAPIResponseCode.bad_request
                api_response.result = "duplicate attribute"
                _logger.error(api_response.result)
                return api_response.json_response()
            if attr["type"] == "multiple_choice":
                if not re.search(mutli_requirement, attr["value"]):
                    api_response.code = EAPIResponseCode.bad_request
                    api_response.result = "regex value error"
                    _logger.error(api_response.result)
                    return api_response.json_response()
            else:
                if attr["value"] and len(attr["value"]) > 100:
                    api_response.code = EAPIResponseCode.bad_request
                    api_response.result = "text to long"
                    _logger.error(api_response.result)
                    return api_response.json_response()
            attr_data[attr["name"]] = attr["value"]
        valid, error_msg = check_attributes(attr_data)
        if not valid:
            api_response.code = EAPIResponseCode.bad_request
            api_response.result = error_msg
            _logger.error(api_response.result)
            return api_response.json_response()

        required_fields = ["name", "type", "value", "optional"]
        attr_list = []
        # required attrbiute check
        for attribute in attributes:
            attr_data = {
                "manifest_id": manifest.id, 
                "project_code": data.project_code, 
            }
            for field in required_fields:
                if not field in attribute:
                    api_response.code = EAPIResponseCode.bad_request
                    api_response.result = f"Missing required field {field}"
                    _logger.error(api_response.result)
                    return api_response.json_response()
                attr_data[field] = attribute[field]
            # check if connect to any files
            if not attr_data["optional"]:
                response = requests.post(ConfigClass.NEO4J_SERVICE + "nodes/File/query/count", json={"manifest_id": manifest.id})
                if response.json()["count"] > 0:
                    api_response.code = EAPIResponseCode.forbidden
                    api_response.result = "Can't add required attributes to manifest attached to files"
                    _logger.error(api_response.result)
                    return api_response.json_response()
            attr_list.append(attr_data)

        # Create create attributes in psql
        for attr in attr_list:
            attribute = DataAttributeModel(**attr)
            db.session.add(attribute)
            db.session.commit()
            db.session.refresh(attribute)
        api_response.result = "Success"
        return api_response.json_response()


@cbv(router)
class ExportManifest:
    @router.get('/manifest/file/export', summary="Export a data manifest")
    def get(self, manifest_id: int):
        api_response = APIResponse()
        response_data = {
            "attributes": []
        }
        manifest = db.session.query(DataManifestModel).get(manifest_id)
        attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest.id).\
                order_by(DataAttributeModel.id.asc())
        for attribute in attributes:
            response_data["attributes"].append({
                "name": attribute.name,
                "type": attribute.type.value,
                "value": attribute.value,
                "optional": attribute.optional,
            })
        response_data["name"] = manifest.name
        response_data["project_code"] = manifest.project_code
        return response_data


@cbv(router)
class FileManifestQuery:
    @router.post('/manifest/query', response_model=manifest.POSTQueryResponse, summary="Query file manifests")
    def post(self, data: manifest.POSTQueryRequest):
        api_response = APIResponse()
        geid_list = data.geid_list
        lineage_view = data.lineage_view

        results = {} 
        for geid in geid_list:
            file_node = get_file_node_bygeid(geid)
            if not file_node:
                file_node = get_trashfile_node_bygeid(geid)

            if file_node and file_node.get("manifest_id"):
                attributes = []
                manifest_id = file_node["manifest_id"]
                manifest = db.session.query(DataManifestModel).get(manifest_id)
                sql_attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest_id)
                for sql_attribute in sql_attributes:
                    attributes.append({
                        "id": sql_attribute.id,
                        "name": sql_attribute.name,
                        "manifest_name": manifest.name,
                        "value": file_node.get("attr_" + sql_attribute.name, ""),
                        "type": sql_attribute.type.value,
                        "optional": sql_attribute.optional,
                        "manifest_id": manifest_id,
                    })
                results[geid] = attributes 
            else:
                results[geid] = {} 
        api_response.result = results
        return api_response.json_response()
