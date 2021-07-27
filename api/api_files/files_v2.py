from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models import files as models
from models.base_models import EAPIResponseCode
from config import ConfigClass
import requests
import math

router = APIRouter()

@cbv(router)
class DatasetFileQueryV2:
    # @router.post('/{dataset_id}/query', response_model=models.DatasetFileQueryPOSTResponse, summary="Query on files by dataset")
    @router.post('/{project_geid}/query', response_model=models.DatasetFileQueryPOSTResponse,
                 summary="Query on files by dataset")
    # async def post(self, dataset_id, data: models.DatasetFileQueryPOSTV2):
    async def post(self, project_geid, data: models.DatasetFileQueryPOSTV2):
        api_response = models.DatasetFileQueryPOSTResponse()
        page = data.page
        page_size = data.page_size
        order_type = data.order_type
        if order_type and not order_type.lower() in ["desc", "asc"]:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid order_type"
            return api_response.json_response()
        page_kwargs = {
            "order_by": "list_priority ASC,end_node." + data.order_by,
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

        try:
            query_params ={
                "global_entity_id": project_geid
            }
            container_id = get_container_id(query_params)
            response = requests.get(ConfigClass.NEO4J_SERVICE + f"nodes/Container/node/{container_id}")
            if response.status_code != 200:
                error_msg = response.json()
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f"Neo4j error: {error_msg}"
                return api_response.json_response()
            dataset = response.json()[0]
        except Exception as e:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = "Neo4j error: " + str(e)
            return api_response.json_response()


        for label in labels:
            if not "Folder" in label and not "TrashFile" in label:
                if not query.get(label):
                    query[label] = {}
                query[label]["is_root"] = True

        relation_payload = {
            **page_kwargs,
            "start_label": "Container",
            "end_labels": labels,
            "query": {
                "start_params": {"code": dataset["code"]}, 
                "end_params": query, 
            },
        }
        try:
            response = requests.post(ConfigClass.NEO4J_SERVICE_V2 + "relations/query", json=relation_payload)
            if response.status_code != 200:
                error_msg = response.json()
                api_response.code = EAPIResponseCode.internal_error
                api_response.error_msg = f"Neo4j error: {error_msg}"
                return api_response.json_response()
            nodes = response.json()
        except Exception as e:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = "Neo4j error: " + str(e)
            return api_response.json_response()

        total = response.json()["total"]
        api_response.result = nodes["results"]
        api_response.total = total 
        api_response.page = page 
        api_response.num_of_pages = math.ceil(total / page_size) 
        return api_response.json_response()


@cbv(router)
class FolderFileQueryV2:
    @router.post('/folder/{folder_geid}/query', response_model=models.DatasetFileQueryPOSTResponse, summary="Query on files by dataset")
    async def post(self, folder_geid, data: models.DatasetFileQueryPOSTV2):
        api_response = models.DatasetFileQueryPOSTResponse()
        page = data.page
        page_size = data.page_size
        order_type = data.order_type
        if order_type and not order_type.lower() in ["desc", "asc"]:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid order_type"
            return api_response.json_response()
        page_kwargs = {
            "order_by": "list_priority ASC,end_node." + data.order_by,
            "order_type": order_type,
            "skip": page * page_size,
            "limit": page_size
        }
        query = data.query
        if not query:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Missing required attribute query"
            return api_response.json_response()

        labels = query.pop("labels", None)
        if not labels:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Missing required attribute labels"
            return api_response.json_response()

        relation_payload = {
            **page_kwargs,
            "start_label": "Folder",
            "end_labels": labels,
            "query": {
                "start_params": {"global_entity_id": folder_geid}, 
                "end_params": query, 
            },
        }
        response = requests.post(ConfigClass.NEO4J_SERVICE_V2 + "relations/query", json=relation_payload)
        nodes = response.json()

        total = response.json()["total"]
        api_response.result = nodes["results"]
        api_response.total = total 
        api_response.page = page 
        api_response.num_of_pages = math.ceil(total / page_size) 
        return api_response.json_response()


def get_container_id(query_params):
    url = ConfigClass.NEO4J_SERVICE + f"nodes/Container/query"
    payload = {
        **query_params
    }
    result = requests.post(url, json=payload)
    if result.status_code != 200 or result.json() == []:
        return None
    result = result.json()[0]
    container_id = result["id"]
    return str(container_id)
