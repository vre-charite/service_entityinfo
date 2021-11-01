from pydantic import BaseModel, Field
from models.base_models import APIResponse, PaginationRequest

class AttachAttributesPOST(BaseModel):
    manifest_id: str
    global_entity_id: list
    attributes: dict


class AttachPOSTResponse(APIResponse):
    result: dict = Field({}, example={
           'code': 200,
           'error_msg': '',
           'num_of_pages': 10,
           'page': 1,
           'result': [{   
                "name":"neo4j entity name",
                "geid":"0f49696b-5fcf-480b-bfd4-543858e4d3e7-1620666366",
                "display_path":"xxxx",
                "operation_status":"TERMINATED",
                "error_type":"attributes_duplicate /internal_error"
            }],
            'total': 67
        }
    )
