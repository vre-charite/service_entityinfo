# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

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
