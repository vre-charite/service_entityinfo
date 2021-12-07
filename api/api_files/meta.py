import math
import json
import requests
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from models.meta import MetaGET, MetaGETResponse, get_parent_connections, GETFileDetail, POSTFileDetail, \
        POSTFileDetailResponse
from models.base_models import EAPIResponseCode, APIResponse
from config import ConfigClass
from .utils import get_source_label, get_query_labels, convert_query

router = APIRouter()


@cbv(router)
class FileBulkDetail:
    @router.post('/bulk/detail', response_model=POSTFileDetailResponse, summary="Get files by geid")
    async def post(self, data: POSTFileDetail):
        api_response = APIResponse()
        if not data.geids:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "geids is required"
            return api_response.json_response()

        try:
            response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/query/geids", json={"geids": data.geids})
        except Exception as e:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = "Neo4j error: " + str(e)
            return api_response.json_response()

        return response.json()


@cbv(router)
class FileDetail:
    @router.get('/detail/{file_geid}', response_model=GETFileDetail, summary="Get detail of single file by geid")
    async def get(self, file_geid):
        api_response = APIResponse()
        try:
            response = requests.get(ConfigClass.NEO4J_SERVICE + f"nodes/geid/{file_geid}")
        except Exception as e:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = "Neo4j error: " + str(e)
            return api_response.json_response()

        if not response.json():
            api_response.code = EAPIResponseCode.not_found
            api_response.error_msg = "File not found"
            return api_response.json_response()
        api_response.result = response.json()[0]
        return api_response.json_response()


@cbv(router)
class FileMeta:
    @router.get('/meta/{geid}', response_model=MetaGETResponse, summary="Query on files by dataset or folder")
    async def get(self, geid, params: MetaGET = Depends(MetaGET)):
        """
            Get and filter file meta from Neo4j given a Dataset or Folder geid
        """
        api_response = MetaGETResponse()
        page = params.page
        page_size = params.page_size
        order_type = params.order_type
        if order_type and not order_type.lower() in ["desc", "asc"]:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid order_type"
            return api_response.json_response()
        page_kwargs = {
            "order_by": "list_priority ASC,end_node." + params.order_by,
            "order_type": order_type,
            "skip": page * page_size,
            "limit": page_size
        }
        source_type = params.source_type
        zone = params.zone
        routing = [] # folder and subfolders path routing
        if params.partial:
            partial = json.loads(params.partial)
        else:
            partial = []

        if params.query:
            query = json.loads(params.query)
        else:
            query = {}

        start_label = get_source_label(source_type)
        if not start_label:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid source_type"
            return api_response.json_response()

        labels = get_query_labels(zone, source_type)
        if not labels:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid zone"
            return api_response.json_response()

        neo4j_query = convert_query(labels, query, partial, source_type)

        relation_payload = {
            **page_kwargs,
            "start_label": start_label,
            "end_labels": labels,
            "query": {
                "start_params": {"global_entity_id": geid},
                "end_params": neo4j_query,
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

            # get routing
            routing = get_parent_connections(geid)

        except Exception as e:
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = "Neo4j error: " + str(e)
            return api_response.json_response()

        total = response.json()["total"]
        api_response.result = {
            "data": nodes["results"],
            "routing": routing
        }
        api_response.total = total
        api_response.page = page
        api_response.num_of_pages = math.ceil(total / page_size)
        return api_response.json_response()
