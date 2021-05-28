from pydantic import BaseModel, Field
from models.base_models import APIResponse, PaginationRequest
from config import ConfigClass
import requests


class CheckFileResponse(APIResponse):
    result: dict = Field({}, example={
                "code": 200,
                "error_msg": "",
                "page": 0,
                "total": 1,
                "num_of_pages": 1,
                "result": [
                    {
                        "id": 2942,
                        "labels": [
                            "File",
                            "Greenroom"
                        ],
                        "global_entity_id": "77b04c69-e79d-4c63-a914-7942e1555ec3-1620825051",
                        "project_code": "may511",
                        "file_size": 1145,
                        "operator": "admin",
                        "tags": [],
                        "archived": 'false',
                        "list_priority": 20,
                        "path": "/data/vre-storage/may511/raw/folders1",
                        "time_lastmodified": "2021-05-12T13:10:52",
                        "uploader": "admin",
                        "process_pipeline": "",
                        "parent_folder_geid": "c1c3766f-36bd-42db-8ca5-9040726cbc03-1620764271",
                        "name": "test.zip",
                        "time_created": "2021-05-12T13:10:52",
                        "guid": "9fc4353b-c4d3-4d29-aa11-d04688f4abc7",
                        "full_path": "/data/vre-storage/may511/raw/folders1/test.zip",
                        "generate_id": "undefined"
                    }
                ]
            }
    )


def http_query_node(query_params={}):
    payload = {
        **query_params
    }
    node_query_url = ConfigClass.NEO4J_SERVICE + "nodes/Dataset/query"
    response = requests.post(node_query_url, json=payload)
    return response
