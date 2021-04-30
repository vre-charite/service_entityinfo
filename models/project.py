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
        "result": {
            "id": 2077,
            "labels": [
                "File",
                "Greenroom",
                "Raw"
            ],
            "global_entity_id": "file_data-2a7ea1d8-7dea-11eb-8428-be498ca98c54-1614973025",
            "operator": "",
            "file_size": 1048576,
            "tags": [],
            "archived": "false",
            "path": "/data/vre-storage/mar04/raw",
            "time_lastmodified": "2021-03-05T19:37:06",
            "uploader": "admin",
            "process_pipeline": "",
            "name": "Testdateiäöüßs4",
            "time_created": "2021-03-05T19:37:06",
            "guid": "f91b258d-2f1d-409a-9551-91af8057e70e",
            "full_path": "/data/vre-storage/mar04/raw/Testdateiäöüßs4",
            "generate_id": "undefined"
        }
    }
    )


def http_query_node(query_params={}):
    payload = {
        **query_params
    }
    node_query_url = ConfigClass.NEO4J_HOST + "/v1/neo4j/nodes/Dataset/query"
    response = requests.post(node_query_url, json=payload)
    return response
