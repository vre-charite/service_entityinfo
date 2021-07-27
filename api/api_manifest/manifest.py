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
        #page = int(request.args.get('page', 1))
        #page_size = int(request.args.get('page_size', 25))
        if not project_code:
            my_res.code = EAPIResponseCode.bad_request
            my_res.result = "project_code is required"
            _logger.error(my_res.result)
            return my_res.json_response()

        # Query psql for manifests
        # paginated
        #manifests = db.session.query(DataManifestModel).filter_by(
        #        project_code=project_code).paginate(page=page, per_page=page_size, error_out=False)
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
class RestfulAttributes:
    @router.post('/attributes', response_model=manifest.POSTAttributesResponse, summary="Bulk create attributes")
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
    @router.put('/attribute/{attribute_id}', response_model=manifest.POSTAttributesResponse, summary="Update an attribute")
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

    @router.delete('/attribute/{attribute_id}', response_model=manifest.DELETEAttributeResponse, summary="Delete an attribute")
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


@cbv(router)
class FileManifests:
    @router.post('/file/manifest/attach', response_model=manifest.POSTAttachResponse, summary="Attach a manifest to a file")
    def post(self, data: manifest.POSTAttachRequest):
        """
            Attach file manifest
        """
        api_response = APIResponse()
        manifests = data.manifests
        results = {
            "error": [],
            "success": []
        }
        error_list = []

        for data in manifests:
            # Check required fields
            if not "global_entity_id" in data:
                results["error"].append(data.get("global_entity_id", ""))
                print("missing global_entity_id")
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = "missing global_entity_id"
                _logger.error(api_response.error_msg)
                return api_response.json_response()

            global_entity_id = data["global_entity_id"]
            manifest_id = data.get("manifest_id", None)
            if not manifest_id:
                if not "manifest_name" in data or not "project_code" in data:
                    results["error"].append(data["name"])
                    print("missing manifest id or manifest_name and project_code")
                    api_response.code = EAPIResponseCode.bad_request
                    api_response.error_msg = "missing manifest id or manifest_name and project_code"
                    _logger.error(api_response.error_msg)
                    return api_response.json_response()

                manifest = db.session.query(DataManifestModel).filter_by(name=data["manifest_name"], project_code=data["project_code"]).first()
                manifest_id = manifest.id
            if not manifest_id:
                results["error"].append(data["name"])
                print("Manifest not found")
                api_response.code = EAPIResponseCode.not_found
                api_response.error_msg = "Manifest not found"
                _logger.error(api_response.error_msg)
                return api_response.json_response()

            file_node = get_file_node_bygeid(global_entity_id)
            if not file_node:
                results["error"].append(data["name"])
                print("File not found")
                api_response.code = EAPIResponseCode.not_found
                api_response.error_msg = "File not found"
                _logger.error(api_response.error_msg)
                return api_response.json_response()
            # Make sure it's Greenroom/Raw
            if not is_greenroom(file_node):
                results["error"].append(file_node["name"])
                print("not greenroom")
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = "File is not in greenroom"
                _logger.error(api_response.error_msg)
                return api_response.json_response()

            post_data = {
                "manifest_id": manifest_id,
            }
            attributes = []
            manifest = db.session.query(DataManifestModel).get(manifest_id)

            for key, value in data.get("attributes", {}).items():
                post_data["attr_" + key] = value

                sql_attribute = db.session.query(DataAttributeModel).filter_by(name=key, manifest_id=manifest_id)
                #sql_attribute = sql_attribute[0]
                sql_attribute = sql_attribute.first()
                if sql_attribute.type.value == 'multiple_choice':
                    attribute_value = []
                    attribute_value.append(value)

                    attributes.append({
                        "attribute_name": key,
                        "name": manifest.name,
                        "value": attribute_value
                    })
                else:
                    attributes.append({
                        "attribute_name": key,
                        "name": manifest.name,
                        "value": value
                    })

            # Check required attributes 
            valid, error_msg = has_valid_attributes(manifest_id, data)
            if not valid:
                results["error"].append(file_node["name"])
                print("Mising required attributes")
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = "Mising required attributes"
                _logger.error(api_response.error_msg)
                return api_response.json_response()

            file_id = file_node["id"]
            response = requests.put(ConfigClass.NEO4J_SERVICE + f"nodes/File/node/{file_id}", json=post_data)
            results["success"].append(file_node["name"])

            # Update Elastic Search Entity
            es_payload = {
                "global_entity_id": file_node["global_entity_id"],
                "updated_fields": {
                    "attributes": attributes,
                    "time_lastmodified": time.time()
                }
            }
            es_res = requests.put(ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=es_payload)
            if es_res.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f"Elastic Search Error: {es_res.json()}"
                _logger.error(api_response.error_msg)
                return api_response.json_response()


        api_response.result = results
        return api_response.json_response()

@cbv(router)
class FileManifest:
    # @router.put('/file/manifest', response_model=manifest.PUTAttachResponse, summary="Edit attached manifest")
    @router.put('/file/{file_geid}/manifest', response_model=manifest.PUTAttachResponse,
                summary="Edit attached manifest")
    def put(self, request: dict, file_geid: str, ):
        api_response = APIResponse()
        data = request

        # file_node = get_file_node_bygeid(data["global_entity_id"])
        file_node = get_file_node_bygeid(file_geid)
        # data.pop("global_entity_id")
        manifest_obj = db.session.query(DataManifestModel).get(file_node["manifest_id"])

        # Check required attributes
        attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=file_node["manifest_id"]). \
            order_by(DataAttributeModel.id.asc())
        valid_attributes = []
        es_attributes = []
        for attr in attributes:
            valid_attributes.append(attr.name)
            if not attr.optional and not attr.name in data:
                api_response.result = "Missing required attribute"
                api_response.code = EAPIResponseCode.bad_request
                _logger.error(api_response.result)
                return api_response.json_response()
            if attr.type.value == "multiple_choice":
                if not data[attr.name] in attr.value.split(","):
                    if not data[attr.name] and attr.optional:
                        continue
                    api_response.result = "Invalid attribute value"
                    api_response.code = EAPIResponseCode.bad_request
                    _logger.error(api_response.result)
                    return api_response.json_response()
                attribute_value = []
                attribute_value.append(data[attr.name])
                es_attributes.append({
                    "attribute_name": attr.name,
                    "name": manifest_obj.name,
                    "value": attribute_value
                })
            if attr.type.value == "text":
                value = data[attr.name]
                if value:
                    if len(value) > 100:
                        api_response.result = "text to long"
                        api_response.code = EAPIResponseCode.bad_request
                        _logger.error(api_response.result)
                        return api_response.json_response()
                    es_attributes.append({
                        "attribute_name": attr.name,
                        "name": manifest_obj.name,
                        "value": value
                    })
        post_data = {
            "manifest_id": file_node["manifest_id"],
        }
        for key, value in data.items():
            if key not in valid_attributes:
                api_response.result = "Not a valid attribute"
                api_response.code = EAPIResponseCode.bad_request
                _logger.error(api_response.result)
                return api_response.json_response()
            post_data["attr_" + key] = value

        file_id = file_node["id"]
        response = requests.put(ConfigClass.NEO4J_SERVICE + f"nodes/File/node/{file_id}", json=post_data)
        api_response.result = response.json()[0]

        # Update Elastic Search Entity
        es_payload = {
            "global_entity_id": file_node["global_entity_id"],
            "updated_fields": {
                "attributes": es_attributes,
                "time_lastmodified": time.time()
            }
        }
        es_res = requests.put(ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=es_payload)
        if es_res.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f"Elastic Search Error: {es_res.json()}"
            _logger.error(api_response.error_msg)
            return api_response.json_response()

        return api_response.json_response()


@cbv(router)
class ValidateManifest:
    @router.post('/file/manifest/validate', response_model=manifest.POSTValidateResponse, summary="Validate the input to attach a file manifest")
    def post(self, data: manifest.POSTValidateRequest):
        api_response = APIResponse()
        manifest_name = data.manifest_name
        project_code = data.project_code
        manifest = db.session.query(DataManifestModel).filter_by(project_code=project_code, name=manifest_name).first()
        if not manifest:
            api_response.code = EAPIResponseCode.not_found
            api_response.result = f"Manifest not found"
            _logger.error(api_response.result)
            return api_response.json_response()

        attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest.id)
        valid_attributes = []
        for attr in attributes:
            valid_attributes.append(attr.name)

        attributes = data.attributes or {}
        for key, value in attributes.items():
            if key not in valid_attributes:
                api_response.code = EAPIResponseCode.bad_request
                api_response.result = "Invalid attribute"
                _logger.error(api_response.result)
                return api_response.json_response()

        valid, error_msg = check_attributes(attributes)
        if not valid:
            api_response.code = EAPIResponseCode.bad_request
            api_response.result = error_msg
            _logger.error(api_response.result)
            return api_response.json_response()

        # Check required attributes 
        valid, error_msg = has_valid_attributes(manifest.id, data.__dict__)
        if not valid:
            api_response.result = error_msg
            api_response.code = EAPIResponseCode.bad_request
            _logger.error(api_response.result)
            return api_response.json_response()
        api_response.result = "Success"
        return api_response.json_response()


@cbv(router)
class ImportManifest:
    @router.post('/file/manifest/import', response_model=manifest.POSTImportResponse, summary="Import a data manifest")
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
    @router.get('/file/manifest/export', summary="Export a data manifest")
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
