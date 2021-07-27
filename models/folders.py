from pydantic import BaseModel, Field
from models.base_models import APIResponse, PaginationRequest
from typing import List, Optional
from resources import helpers
import requests
from config import ConfigClass
from commons.service_logger.logger_factory_service import SrvLoggerFactory

_logger = SrvLoggerFactory("folder_model").get_logger()


class FoldersPOST(BaseModel):
    '''
    global_entity_id will auto generate if not provided
    '''
    global_entity_id: Optional[str] = None
    folder_name: str
    folder_level: int
    folder_parent_geid: str
    folder_parent_name: str
    uploader: str
    folder_relative_path: str
    zone: str = "greenroom | vrecore"
    project_code: str
    folder_tags: List[str] = []
    extra_labels: List[str] = []
    extra_attrs: dict = {}


class FoldersPOSTResponse(APIResponse):
    '''
    Pre upload response class
    '''
    result: dict = Field({}, example={
        "id": 4624,
        "labels": [
            "Folder",
            "Greenroom"
        ],
        "name": "test4",
        "time_created": "2021-03-19T14:15:00",
        "time_lastmodified": "2021-03-19T14:15:00",
        "global_entity_id": "7dd42578-88bd-11eb-893a-eaff9e667817-1616163300",
        "folder_level": 0,
        "folder_relative_path": "test",
        "project_code": "test created by zhengyang",
        "tags": [
            "test_created_by_zhengyang"
        ],
        "priority": 0,
        "uploader": "testzy"
    }
    )


class FoldersGETResponse(APIResponse):
    '''
    Pre upload response class
    '''
    result: dict = Field({}, example={
        "data": [
            {
                "id": 4673,
                "labels": [
                    "Greenroom",
                    "Folder"
                ],
                "global_entity_id": "ed1a1ed6-8b3a-11eb-be94-eaff9e667817-1616437076",
                "folder_level": 3,
                "folder_relative_path": "a/e/c",
                "time_lastmodified": "2021-03-22T18:17:56",
                "uploader": "zhengyang",
                "name": "d",
                "time_created": "2021-03-22T18:17:56",
                "project_code": "gregtest",
                "priority": 0,
                "tags": []
            },
            {
                "id": 4640,
                "labels": [
                    "Greenroom",
                    "Folder"
                ],
                "global_entity_id": "ec678d8e-8b3a-11eb-99fe-eaff9e667817-1616437075",
                "folder_level": 3,
                "folder_relative_path": "a/b/c",
                "time_lastmodified": "2021-03-22T18:17:55",
                "uploader": "zhengyang",
                "name": "d",
                "time_created": "2021-03-22T18:17:55",
                "project_code": "gregtest",
                "priority": 0,
                "tags": []
            }
        ],
        "routing": [
            {
                "id": 4693,
                "labels": [
                    "Greenroom",
                    "Folder"
                ],
                "global_entity_id": "eb4e43ac-8b3a-11eb-99fe-eaff9e667817-1616437073",
                "folder_level": 1,
                "folder_relative_path": "a",
                "time_lastmodified": "2021-03-22T18:17:53",
                "uploader": "zhengyang",
                "name": "b",
                "time_created": "2021-03-22T18:17:53",
                "project_code": "gregtest",
                "priority": 0,
                "tags": []
            },
            {
                "id": 4690,
                "labels": [
                    "Greenroom",
                    "Folder"
                ],
                "global_entity_id": "eb247a72-8b3a-11eb-be94-eaff9e667817-1616437073",
                "folder_level": 0,
                "folder_relative_path": "",
                "time_lastmodified": "2021-03-22T18:17:53",
                "uploader": "zhengyang",
                "name": "a",
                "time_created": "2021-03-22T18:17:53",
                "project_code": "gregtest",
                "priority": 0,
                "tags": []
            },
            {
                "id": 21,
                "labels": [
                    "Container"
                ],
                "global_entity_id": "dataset-4f640b7e-85be-11eb-99fe-eaff9e667817-1615833798",
                "path": "gregtest",
                "code": "gregtest",
                "time_lastmodified": "2021-03-15T18:43:18",
                "system_tags": [
                    "copied-to-core"
                ],
                "discoverable": True,
                "name": "gregtest",
                "time_created": "2021-02-01T16:04:13",
                "description": "test",
                "type": "Usecase"
            },
            {
                "id": 4637,
                "labels": [
                    "Greenroom",
                    "Folder"
                ],
                "global_entity_id": "ebba4426-8b3a-11eb-8a88-eaff9e667817-1616437074",
                "folder_level": 2,
                "folder_relative_path": "a/b",
                "time_lastmodified": "2021-03-22T18:17:54",
                "uploader": "zhengyang",
                "name": "c",
                "time_created": "2021-03-22T18:17:54",
                "project_code": "gregtest",
                "priority": 0,
                "tags": []
            }
        ]
    }
    )


class FoldersQueryResponse(APIResponse):
    '''
    Pre upload response class
    '''
    result: dict = Field({}, example=[
        {
            "id": 4624,
            "labels": [
                "Folder",
                "Greenroom"
            ],
            "name": "test4",
            "time_created": "2021-03-19T14:15:00",
            "time_lastmodified": "2021-03-19T14:15:00",
            "global_entity_id": "7dd42578-88bd-11eb-893a-eaff9e667817-1616163300",
            "folder_level": 0,
            "folder_relative_path": "test",
            "project_code": "test created by zhengyang",
            "tags": [
                "test_created_by_zhengyang"
            ],
            "priority": 0,
            "uploader": "testzy"
        }
    ]
    )


def http_post_node(node_dict: dict, geid=None):
    '''
    will assign the geid automaticly
    '''
    if not geid:
        node_dict["global_entity_id"] = helpers.get_geid()
    node_creation_url = ConfigClass.NEO4J_SERVICE + "nodes/Folder"
    response = requests.post(node_creation_url, json=node_dict)
    return response


def http_query_node(namespace, query_params={}):
    payload = {
        **query_params
    }
    node_query_url = ConfigClass.NEO4J_SERVICE + "nodes/Folder/query"
    response = requests.post(node_query_url, json=payload)
    return response


def link_folder_parent(namespace, parent_folder_geid, child_folder_geid):
    '''
    link folder parent
    '''
    respon_parent_folder_query = http_query_node(
        namespace, {"global_entity_id": parent_folder_geid})
    if not respon_parent_folder_query.status_code == 200:
        raise(Exception("[respon_parent_folder_query Error] {} {}".format(
            respon_parent_folder_query.status_code, respon_parent_folder_query.text)))
    parent_folder_node = respon_parent_folder_query.json()
    if not parent_folder_node:
        raise(Exception("[respon_parent_folder_query Error] Not found {} {}".format(
            respon_parent_folder_query.status_code, parent_folder_geid)))
    parent_folder_node = parent_folder_node[0]
    respon_child_folder_query = http_query_node(
        namespace, {"global_entity_id": child_folder_geid})
    if not respon_child_folder_query.status_code == 200:
        raise(Exception("[respon_child_folder_query Error] {} {}".format(
            respon_child_folder_query.status_code, respon_child_folder_query.text)))
    child_folder_node = respon_child_folder_query.json()
    if not child_folder_node:
        raise(Exception("[respon_child_folder_query Error] Not found {} {}".format(
            respon_child_folder_query.status_code, child_folder_geid)))
    child_folder_node = child_folder_node[0]
    relation_payload = {
        "start_id": parent_folder_node["id"], "end_id": child_folder_node["id"]}
    response = requests.post(ConfigClass.NEO4J_SERVICE +
                             "relations/own", json=relation_payload)
    if response.status_code // 100 == 2:
        return response
    else:
        raise(Exception("[link_parent Error] {} {}".format(
            response.status_code, response.text)))


def link_project(namespace, project_code, child_folder_geid):
    payload = {
        "code": project_code
    }
    project_node_query_url = ConfigClass.NEO4J_SERVICE + "nodes/Container/query"
    response_query_project = requests.post(
        project_node_query_url, json=payload)
    _logger.info("request url: {}".format(project_node_query_url))
    _logger.info("request payload: {}".format(payload))
    if not response_query_project.status_code == 200:
        raise(
            Exception('[link_project] Invalid project code: {} {}'.format(project_code, response_query_project.status_code)))
    project = response_query_project.json()
    if not project:
        raise(
            Exception('[link_project] Not found project: {}'.format(project_code)))
    project = project[0]
    respon_child_folder_query = http_query_node(
        namespace, {"global_entity_id": child_folder_geid})
    if not respon_child_folder_query.status_code == 200:
        raise(Exception("[respon_child_folder_query Error] {} {}".format(
            respon_child_folder_query.status_code, respon_child_folder_query.text)))
    child_folder_node = respon_child_folder_query.json()
    if not child_folder_node:
        raise(Exception("[respon_child_folder_query Error] Not found {} {}".format(
            respon_child_folder_query.status_code, child_folder_geid)))
    child_folder_node = child_folder_node[0]
    relation_payload = {
        "start_id": project["id"], "end_id": child_folder_node["id"]}
    response = requests.post(ConfigClass.NEO4J_SERVICE +
                             "relations/own", json=relation_payload)
    if response.status_code // 100 == 2:
        return response
    else:
        raise(Exception("[link_project Error] {} {}".format(
            response.status_code, response.text)))
