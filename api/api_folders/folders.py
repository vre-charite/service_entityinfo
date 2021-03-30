from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from commons.logger_services.logger_factory_service import SrvLoggerFactory
from models import folders as models
from models.base_models import EAPIResponseCode
from resources.error_handler import catch_internal
from config import ConfigClass
import requests
import math
import copy
import json

router = APIRouter()
_API_NAMESPACE = "api_folder_nodes"


@cbv(router)
class FolderNodes:
    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.post('/folders', response_model=models.FoldersPOSTResponse, summary="Folder Nodes Restful")
    @catch_internal(_API_NAMESPACE)
    async def post(self, request_payload: models.FoldersPOST):
        '''
        Post function to create entity
        '''
        self._logger.info(f"folder payload: {request_payload.__dict__}")
        api_response = models.APIResponse()
        if not request_payload.zone in ["vrecore", "greenroom"]:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid zone parameter"
            return api_response.json_response()
        namespace = {
            "vrecore": "VRECore",
            "greenroom": "Greenroom"
        }.get(request_payload.zone)
        new_node = {
            "global_entity_id": request_payload.global_entity_id,
            "name": request_payload.folder_name,
            "folder_level": request_payload.folder_level,
            "folder_relative_path": request_payload.folder_relative_path,
            "project_code": request_payload.project_code,
            "tags": request_payload.folder_tags,
            "list_priority": 10,
            "extra_labels": [namespace],
            "uploader": request_payload.uploader,
        }
        result_create_node = models.http_post_node(
            new_node, request_payload.global_entity_id)
        if result_create_node.status_code == 200:
            node_created = result_create_node.json()[0]
            # if not root node folder
            if request_payload.folder_relative_path:
                models.link_folder_parent(
                    namespace, request_payload.folder_parent_geid, node_created['global_entity_id']
                )
            else:
                models.link_project(
                    namespace, request_payload.project_code, node_created['global_entity_id']
                )
            api_response.code = EAPIResponseCode.success
            api_response.result = node_created
            return api_response.json_response()
        else:
            raise("Create failed" + result_create_node.text)

    @router.get('/folder/{geid}', response_model=models.FoldersGETResponse, summary="Folder Nodes Restful")
    @catch_internal(_API_NAMESPACE)
    async def get(self, geid, query="{}",
                  page=0, page_size=10, order_by="time_created",
                  order_type="desc", partial=True, entity_type=['File', 'Folder'],
                  zone='Greenroom',
                  datatype='Raw'):
        '''
        Get function to get the entity by geid, currently not developped. please use another one instead
        Get /v1/project/${project_code}/home
        '''
        api_response = models.APIResponse()

        if order_type and not order_type.lower() in ["desc", "asc"]:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid order_type"
            return api_response.json_response()

        query = json.loads(query)

        query_keys = list(query.keys())

        if len(query_keys) > 0:
            query['partial'] = query_keys
            # query['case_insensitive'] = query_keys

        page_kwargs = {
            "order_by": "list_priority ASC, end_node.{} {}".format(order_by, order_type),
            'limit': int(page_size),
            'skip': int(page) * int(page_size),
        }

        query_payload = {
            **page_kwargs,
            'start_label': "{}:Folder".format(zone),
            'end_labels': ["{}:{}:File".format(zone, datatype),
                           "{}:Folder".format(zone)],
            'query': {
                'start_params': {
                    'global_entity_id': geid,
                },
                'end_params': {
                    "{}:{}:File".format(zone, datatype): query,
                    "{}:Folder".format(zone): query
                },
            }
        }

        # print(query_payload)

        # get data
        response_query = requests.post(
            ConfigClass.NEO4J_HOST + '/v2/neo4j/relations/query', json=query_payload)
        data = []
        if response_query.status_code == 200:
            data = response_query.json()['results']
        else:
            raise(Exception('[v2 query] {}, {}'.format(
                response_query.status_code, response_query.text)))

        # get routing
        response_routing = requests.get(
            ConfigClass.NEO4J_HOST + '/v1/neo4j/relations/connected/{}'.format(geid))
        routing = []
        if response_routing.status_code == 200:
            routing = response_routing.json()['result']
        else:
            raise(Exception('[v2 connected query] {}, {}'.format(
                response_routing.status_code, response_routing.text)))

        # add self node, if not returned by neo4j
        if len([route for route in routing if route['global_entity_id'] == geid]) == 0:
            self_query_payload = {
                "global_entity_id": geid
            }
            self_query_respon = models.http_query_node(
                "doesnotmatterforgeidquery", self_query_payload)
            if self_query_respon.status_code == 200:
                routing = routing + self_query_respon.json()
            else:
                raise(Exception('[v2 routing query] {}, {}'.format(
                    self_query_respon.status_code, self_query_respon.text)))

        total = int(response_query.json()["total"])

        # return response
        api_response.code = EAPIResponseCode.success
        api_response.total = total
        api_response.page = int(page)
        api_response.num_of_pages = math.ceil(total / int(page_size))
        api_response.result = {
            "data": data,
            "routing": routing
        }
        return api_response.json_response()

    @ router.get('/folders', response_model=models.FoldersQueryResponse, summary="Folder Nodes Restful")
    @ catch_internal(_API_NAMESPACE)
    async def query(self, zone, project_code, folder_relative_path=None, uploader=None):
        '''
        Get function to query the entity by condition
        '''
        api_response = models.APIResponse()
        if not zone in ["vrecore", "greenroom"]:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = "Invalid zone parameter"
            return api_response.json_response()
        namespace = {
            "vrecore": "VRECore",
            "greenroom": "Greenroom"
        }.get(zone)
        query_payload = {
            "project_code": project_code
        }
        if folder_relative_path:
            query_payload["folder_relative_path"] = folder_relative_path
        if uploader:
            query_payload["uploader"] = uploader
        query_respon = models.http_query_node(namespace, query_payload)
        if query_respon.status_code == 200:
            api_response.code = EAPIResponseCode.success
            api_response.result = query_respon.json()
            return api_response.json_response()
        else:
            raise(Exception("query_respon: {}, {}".format(
                query_respon.status_code, query_respon.text)))
