from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models import files as models
from models.base_models import EAPIResponseCode
from models import folders as folder_models
from resources.error_handler import catch_internal
from commons.logger_services.logger_factory_service import SrvLoggerFactory
from config import ConfigClass
import requests
import math
import time

router = APIRouter()
_API_NAMESPACE = "file_entity_restful"


@cbv(router)
class CreateFile:
    def __init__(self):
        self._logger = SrvLoggerFactory('api_file').get_logger()

    @router.post('/', response_model=models.CreateFilePOSTResponse, summary="Create file")
    @catch_internal(_API_NAMESPACE)
    async def post(self, data: models.CreateFilePOST):
        api_response = models.CreateFilePOSTResponse()
        full_path = data.full_path
        payload = data.__dict__.copy()
        payload["name"] = full_path.split("/")[-1]
        payload["path"] = "/".join(full_path.split("/")[:-1])
        payload["archived"] = False

        self._logger.info(f"file payload: {payload}")

        es_payload = {
            "global_entity_id": payload["global_entity_id"],
            "data_type": "File",
            "operator": payload["uploader"],
            "file_size": payload["file_size"],
            "tags": payload["tags"],
            "archived": False,
            "path": payload["path"],
            "time_lastmodified": time.time(),
            "process_pipeline": payload["process_pipeline"],
            "uploader": payload["uploader"],
            "file_name": payload["name"],
            "time_created": time.time(),
            "atlas_guid": payload["guid"],
            "full_path": payload["full_path"],
            "generate_id": payload["generate_id"],
            "project_code": payload["project_code"],
            "list_priority": 20
        }

        del payload["project_id"]

        if data.input_file_id:
            del payload["input_file_id"]
            if not data.process_pipeline:
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = "Missing required field process_pipeline for input_file_id"
                return api_response.json_response()
            if not data.operator:
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = "Missing required field operator for input_file_id"
                return api_response.json_response()

        extra_labels = []
        if data.namespace == "greenroom":
            extra_labels.append("Greenroom")
            es_payload['zone'] = 'Greenroom'
        else:
            extra_labels.append("VRECore")
            es_payload['zone'] = 'VRECore'

        del payload["namespace"]
        payload["extra_labels"] = extra_labels
        payload["list_priority"] = 20

        # Create node
        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/File", json=payload)
        if response.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f"Neo4j error: {response.json()}"
            return api_response.json_response()
        file_node = response.json()[0]

        if data.parent_folder_geid:
            # Create Folder to File relation
            respon_parent_folder_query = folder_models.http_query_node(
                data.namespace, {"global_entity_id": data.parent_folder_geid})
            if not respon_parent_folder_query.status_code == 200:
                raise(Exception("[respon_parent_folder_query Error] {} {}".format(
                    respon_parent_folder_query.status_code, respon_parent_folder_query.text)))
            parent_folder_node = respon_parent_folder_query.json()
            if not parent_folder_node:
                raise(Exception("[respon_parent_folder_query Error] Not found {} {}".format(
                    respon_parent_folder_query.status_code, data.parent_folder_geid)))
            parent_folder_node = parent_folder_node[0]
            relation_payload = {
                "start_id": parent_folder_node["id"], "end_id": file_node["id"]}
            response = requests.post(
                ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/own", json=relation_payload)
            if response.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f"Neo4j error: {response.json()}"
                return api_response.json_response()
        else:
            # Create Dataset to file relation
            relation_payload = {"start_id": data.project_id,
                                "end_id": file_node["id"]}
            response = requests.post(
                ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/own", json=relation_payload)
            if response.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f"Neo4j error: {response.json()}"
                return api_response.json_response()

        # Create input to processed relation
        # curretly wouldn't be triggered by dataops_util
        if data.input_file_id:
            relation_payload = {
                "start_id": data.input_file_id,
                "end_id": file_node["id"],
                "properties": {"operator": data.operator}}
            self._logger.debug("CreateFile relation_payload: " + str(relation_payload))
            response = requests.post(
                ConfigClass.NEO4J_HOST + f"/v1/neo4j/relations/{data.process_pipeline}", json=relation_payload)
            if response.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f"Neo4j error: {response.json()}"
                return api_response.json_response()

        # Create entity in Elastic Search
        es_res = requests.post(ConfigClass.PROVENANCE_SERVICE + '/v1/entity/file', json=es_payload)
        self._logger.info(f"Elastic Search Result: {es_res.json()}")
        if es_res.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f"Elastic Search Error: {es_res.json()}"
            return api_response.json_response()

        api_response.result = file_node
        return api_response.json_response()


@cbv(router)
class DatasetFileQuery:
    @router.post('/{dataset_id}/query', response_model=models.DatasetFileQueryPOSTResponse, summary="Query on files by dataset")
    async def post(self, dataset_id, data: models.DatasetFileQueryPOST):
        api_response = models.DatasetFileQueryPOSTResponse()
        page = data.page
        page_size = data.page_size
        order_type = data.order_type
        if order_type and not order_type.lower() in ["desc", "asc"]:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid order_type"
            return api_response.json_response()
        page_kwargs = {
            "order_by": data.order_by,
            "order_type": order_type,
            "skip": page * page_size,
            "limit": page_size
        }
        query = data.query
        labels = query.pop("labels", None)
        if not labels:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Missing required attribute labels"
            return api_response.json_response()

        if not query:
            query = None

        relation_payload = {
            **page_kwargs,
            "label": "own",
            "start_label": "Dataset",
            "end_label": labels,
            "start_params": {"id": int(dataset_id)},
            "end_params": query,
            "partial": data.partial
        }
        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/query", json=relation_payload)
        nodes = [x["end_node"] for x in response.json()]

        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/query/count", json=relation_payload)
        total = response.json()["count"]
        api_response.result = nodes
        api_response.total = total
        api_response.page = page
        api_response.num_of_pages = math.ceil(total / page_size)
        return api_response.json_response()


@cbv(router)
class TrashCreate:
    def __init__(self):
        self._logger = SrvLoggerFactory('api_delete_file').get_logger()

    @router.post('/trash', response_model=models.CreateTrashPOSTResponse, summary="Create TrashFile")
    async def post(self, data: models.CreateTrashPOST):
        api_response = models.CreateTrashPOSTResponse()
        full_path = data.full_path
        trash_full_path = data.trash_full_path
        name = trash_full_path.split("/")[-1]
        trash_path = "/".join(trash_full_path.split("/")[:-1])

        # Get existing File
        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/File/query", json={"full_path": data.full_path})
        file_node = response.json()[0]

        labels = file_node.get("labels")
        labels.remove("File")

        trash_file_data = {
            "name": name,
            "path": trash_path,
            "full_path": trash_full_path,
            "description": file_node.get("description"),
            "file_size": file_node.get("file_size"),
            "guid": file_node.get("guid"),
            "manifest_id": file_node.get("manifest_id", None),
            "generate_id": file_node.get("generate_id"),
            "archived": True,
            "extra_labels": labels,
            "uploader": file_node.get("uploader"),
            "tags": file_node.get("tags"),
            "global_entity_id": data.trash_geid,
        }

        for key, value in file_node.items():
            if key.startswith("attr_"):
                trash_file_data[key] = value

        # Create TrashFile
        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/TrashFile", json=trash_file_data)
        trash_file = response.json()[0]

        # Get dataset
        relation_payload = {
            "label": "own",
            "start_label": "Dataset",
            "end_label": "File",
            "start_params": None,
            "end_params": {"full_path": full_path},
        }
        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/query", json=relation_payload)
        dataset_id = response.json()[0]["start_node"]["id"]

        # Create File to TrashFile relation
        relation_payload = {
            "start_id": file_node["id"], "end_id": trash_file["id"],
            "properties": {"operator": file_node.get("operator")}}
        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/deleted", json=relation_payload)
        # Create Dataset to file relation
        relation_payload = {"start_id": dataset_id, "end_id": trash_file["id"]}
        response = requests.post(
            ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/own", json=relation_payload)

        api_response.result = trash_file

        # Update Elastic Search Entity
        es_payload = {
            "global_entity_id": file_node["global_entity_id"],
            "updated_fields": {
                "name": name,
                "path": trash_path,
                "full_path": trash_full_path,
                "archived": True,
                "process_pipeline": "data_delete",
                "time_lastmodified": time.time()
            }
        }
        self._logger.info(f"es delete file payload: {es_payload}")
        es_res = requests.put(ConfigClass.PROVENANCE_SERVICE + '/v1/entity/file', json=es_payload)
        self._logger.info(f"es delete file response: {es_res.text}")
        if es_res.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f"Elastic Search Error: {es_res.json()}"
            return api_response.json_response()

        return api_response.json_response()
