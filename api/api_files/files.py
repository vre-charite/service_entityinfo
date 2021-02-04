from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models import files as models
from models.base_models import EAPIResponseCode
from config import ConfigClass
import requests
import math

router = APIRouter()

@cbv(router)
class CreateFile:
    #def __init__(self):
    #    self._logger = SrvLoggerFactory('api_file').get_logger()

    @router.post('/', response_model=models.CreateFilePOSTResponse, summary="Create file")
    async def post(self, data: models.CreateFilePOST):
        api_response = models.CreateFilePOSTResponse() 
        full_path = data.full_path
        payload = data.__dict__.copy()
        payload["name"] = full_path.split("/")[-1]
        payload["path"] = "/".join(full_path.split("/")[:-1])
        payload["archived"] = False
        del payload["project_id"]

        if data.input_file_id:
            del payload["input_file_id"]

        if data.type == "processed":
            if not data.process_pipeline:
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = "Missing required field process_pipeline"
                return api_response.json_response()
            if not data.operator:
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = "Missing required field operator"
                return api_response.json_response()

        extra_labels = [] 
        if data.namespace == "greenroom":
            extra_labels.append("Greenroom")
        else:
            extra_labels.append("VRECore")

        if data.type == "raw":
            extra_labels.append("Raw")
        else:
            extra_labels.append("Processed")
        del payload["namespace"]
        del payload["type"]
        payload["extra_labels"] = extra_labels

        # Create node
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/File", json=payload)
        if response.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f"Neo4j error: {response.json()}"
            return api_response.json_response()
        file_node = response.json()[0]

        # Create Dataset to file relation
        relation_payload = {"start_id": data.project_id, "end_id": file_node["id"]} 
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/own", json=relation_payload)
        if response.status_code != 200:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = f"Neo4j error: {response.json()}"
            return api_response.json_response()

        # Create input to processed relation
        if data.input_file_id:
            relation_payload = {"start_id": data.input_file_id, "end_id": file_node["id"]} 
            response = requests.post(ConfigClass.NEO4J_HOST + f"/v1/neo4j/relations/{data.process_pipeline}", json=relation_payload)
            if response.status_code != 200:
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f"Neo4j error: {response.json()}"
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
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/query", json=relation_payload)
        nodes = [x["end_node"] for x in response.json()]

        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/query/count", json=relation_payload)
        total = response.json()["count"]
        api_response.result = nodes
        api_response.total = total 
        api_response.page = page 
        api_response.num_of_pages = math.ceil(total / page_size) 
        return api_response.json_response()


@cbv(router)
class TrashCreate:
    @router.post('/trash', response_model=models.CreateTrashPOSTResponse, summary="Create TrashFile")
    async def post(self, data: models.CreateTrashPOST):
        api_response = models.CreateTrashPOSTResponse()
        full_path = data.full_path
        trash_full_path = data.trash_full_path
        name = trash_full_path.split("/")[-1]
        trash_path = "/".join(trash_full_path.split("/")[:-1])

        # Get existing File
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/File/query", json={"full_path": data.full_path})
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
            "process_pipeline": "data_delete",
            "uploader": file_node.get("uploader"),
            "tags": file_node.get("tags"),
            "global_entity_id": data.trash_geid,
        } 
        for key, value in file_node.items():
            if key.startswith("attr_"):
                trash_file_data[key] = value 

        # Create TrashFile
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/TrashFile", json=trash_file_data)
        trash_file = response.json()[0]

        # Get dataset
        relation_payload = {
            "label": "own",
            "start_label": "Dataset",
            "end_label": "File",
            "start_params": None, 
            "end_params": {"full_path": full_path}, 
        }
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/query", json=relation_payload)
        dataset_id = response.json()[0]["start_node"]["id"]

        # Create File to TrashFile relation
        relation_payload = {"start_id": file_node["id"], "end_id": trash_file["id"]} 
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/deleted", json=relation_payload)
        # Create Dataset to file relation
        relation_payload = {"start_id": dataset_id, "end_id": trash_file["id"]} 
        response = requests.post(ConfigClass.NEO4J_HOST + "/v1/neo4j/relations/own", json=relation_payload)

        api_response.result = trash_file
        return api_response.json_response()
