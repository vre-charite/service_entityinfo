from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from commons.service_logger.logger_factory_service import SrvLoggerFactory
from models import folders as models
from models.base_models import EAPIResponseCode
from models.meta import get_parent_connections
from resources.error_handler import catch_internal
from config import ConfigClass
import requests
import math
import copy
import json
import os
import time
from datetime import datetime, timezone

router = APIRouter()
_API_NAMESPACE = "api_folder_nodes"


@cbv(router)
class FolderNodes:
    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.post('/folders/batch', response_model=models.FoldersPOSTResponse, summary="Batch Folder Nodes Restful")
    # @catch_internal(_API_NAMESPACE)
    async def batch_folder(self, request_payload: models.BatchFoldersPOST):
        '''
        Post function to btach create folder
        '''
        self._logger.info(f"folder payload: {request_payload.__dict__}")
        api_response = models.APIResponse()
        payload = request_payload.payload

        namespace = {
            "vrecore": "VRECore",
            "greenroom": "Greenroom"
        }.get(request_payload.zone)
        extra_labels = [namespace]

        nodes_data = []
        relations_data = []

        for item in payload:
            item = dict(item)
            time_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_node = {
                "global_entity_id": item['global_entity_id'],
                "name": item['folder_name'],
                "folder_level": item['folder_level'],
                "folder_relative_path": item['folder_relative_path'],
                "project_code": item['project_code'],
                "tags": item['folder_tags'],
                "list_priority": 10,
                "uploader": item['uploader'],
                "archived": False,
                "display_path": os.path.join(item['folder_relative_path'],
                                             item['folder_name']),
                "time_created": time_now,
                "time_lastmodified": time_now
            }
            if "extra_attrs" in item:
                for k, v in item["extra_attrs"].items():
                    new_node[k] = v

            nodes_data.append(new_node)
            if request_payload.link_container:
                relations_data.append({
                    "start_params": {
                        "code": new_node['project_code']
                    },
                    "end_params": {
                        "project_code": new_node['project_code'],
                        "global_entity_id": new_node["global_entity_id"]
                    }
                })

            if not request_payload.link_container and len(new_node['folder_relative_path']):
                self._logger.info('create folder in elastic search')
                try:
                    es_body = {
                        "global_entity_id": new_node["global_entity_id"],
                        "zone": namespace,
                        "data_type": "Folder",
                        "operator": new_node['uploader'],
                        "file_size": 0,
                        "tags": new_node['tags'],
                        "archived": False,
                        "location": "",
                        "time_lastmodified": time.time(),
                        "process_pipeline": "",
                        "uploader": new_node['uploader'],
                        "file_name": new_node['name'],
                        "time_created": time.time(),
                        "atlas_guid": "",
                        "display_path": new_node['display_path'],
                        "generate_id": None,
                        "project_code": new_node['project_code'],
                        "priority": 10
                    }

                    es_res = requests.post(
                        ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=es_body)
                    self._logger.info(es_body)
                    self._logger.info(es_res.text)
                    if es_res.status_code != 200:
                        self._logger.error(
                            f"Error while creating folder node in elastic search : {es_res.text}")
                        api_response.code = EAPIResponseCode.internal_error
                        api_response.result = "Error while creating folder node in elastic search"
                        return api_response.json_response()
                except Exception as e:
                    self._logger.error(
                        "Error while call elastic search" + str(e))
                    api_response.code = EAPIResponseCode.internal_error
                    api_response.result = "Error while call elastic search" + \
                        str(e)
                    return api_response.json_response()

        result_create_node = models.http_bulk_post_node(
            nodes_data, extra_labels)

        if result_create_node.status_code == 200:
            if relations_data:
                result_link_projects = models.bulk_link_project(
                    ['start', 'end'], 'Container', 'Folder', relations_data)
                if result_link_projects.status_code == 200:
                    api_response.code = EAPIResponseCode.success
                    api_response.result = {"result": "success"}
                else:
                    api_response.code = EAPIResponseCode.internal_error
                    api_response.result = {
                        "result": "failed to link projects with folders"}
        else:
            api_response.code = EAPIResponseCode.internal_error
            api_response.result = {"result": "failed to create folders"}

        return api_response.json_response()

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
        extra_labels = [namespace]
        extra_labels += request_payload.extra_labels
        new_node = {
            "global_entity_id": request_payload.global_entity_id,
            "name": request_payload.folder_name,
            "folder_level": request_payload.folder_level,
            "folder_relative_path": request_payload.folder_relative_path,
            "project_code": request_payload.project_code,
            "tags": request_payload.folder_tags,
            "list_priority": 10,
            "extra_labels": extra_labels,
            "uploader": request_payload.uploader,
            "archived": False,
            "display_path": os.path.join(request_payload.folder_relative_path,
                                         request_payload.folder_name)
        }

        # name folder do not need to be stored in es
        if len(request_payload.folder_relative_path):
            es_body = {
                "global_entity_id": request_payload.global_entity_id,
                "zone": namespace,
                "data_type": "Folder",
                "operator": request_payload.uploader,
                "file_size": 0,
                "tags": request_payload.folder_tags,
                "archived": False,
                "location": "",
                "time_lastmodified": time.time(),
                "process_pipeline": "",
                "uploader": request_payload.uploader,
                "file_name": request_payload.folder_name,
                "time_created": time.time(),
                "atlas_guid": "",
                "display_path": os.path.join(request_payload.folder_relative_path,
                                             request_payload.folder_name),
                "generate_id": None,
                "project_code": request_payload.project_code,
                "priority": 10
            }

            es_res = requests.post(
                ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=es_body)
            if es_res.status_code != 200:
                self._logger.error(
                    f"Error while creating folder node in elastic search : {es_res.text}")
                api_response.code = EAPIResponseCode.internal_error
                api_response.result = "Error while creating folder node in elastic search"
                return api_response.json_response()

        is_trashbin_root = request_payload.extra_attrs.get('is_trashbin_root')
        for k, v in request_payload.extra_attrs.items():
            new_node[k] = v
        self._logger.info(
            f" neo4j folder creation payload:  {new_node}")
        result_create_node = models.http_post_node(
            new_node, request_payload.global_entity_id)
        if result_create_node.status_code == 200:
            node_created = result_create_node.json()[0]
            # if not root node folder
            if request_payload.folder_relative_path and request_payload.folder_parent_geid and not is_trashbin_root:
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
            raise(Exception("Create failed" + result_create_node.text))

    # Deprecated and has been merged into entity listing API
    @router.get('/folder/{geid}', response_model=models.FoldersGETResponse, summary="Folder Nodes Restful",
                deprecated=True)
    @catch_internal(_API_NAMESPACE)
    async def get(self, geid, query="{}",
                  page=0, page_size=10, order_by="time_created",
                  order_type="desc", partial=True, entity_type=['File', 'Folder'],
                  zone='Greenroom',
                  datatype='Raw'):
        '''
        Deprecated and has been merged into entity listing API
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
            ConfigClass.NEO4J_SERVICE_V2 + 'relations/query', json=query_payload)
        data = []
        if response_query.status_code == 200:
            data = response_query.json()['results']
        else:
            raise(Exception('[v2 query] {}, {}'.format(
                response_query.status_code, response_query.text)))

        total = int(response_query.json()["total"])

        # return response
        api_response.code = EAPIResponseCode.success
        api_response.total = total
        api_response.page = int(page)
        api_response.num_of_pages = math.ceil(total / int(page_size))
        api_response.result = {
            "data": data,
            "routing": get_parent_connections(geid)
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
