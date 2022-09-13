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

import httpx
from pydantic import BaseModel
from pydantic import Field

from config import ConfigClass
from models.base_models import APIResponse
from models.base_models import PaginationRequest


class CheckFileResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'code': 200,
            'error_msg': '',
            'page': 0,
            'total': 1,
            'num_of_pages': 1,
            'result': [
                {
                    'id': 2942,
                    'labels': ['File', 'Greenroom'],
                    'global_entity_id': '77b04c69-e79d-4c63-a914-7942e1555ec3-1620825051',
                    'project_code': 'may511',
                    'file_size': 1145,
                    'operator': 'admin',
                    'tags': [],
                    'archived': 'false',
                    'list_priority': 20,
                    'path': '/data/storage/may511/raw/folders1',
                    'time_lastmodified': '2021-05-12T13:10:52',
                    'uploader': 'admin',
                    'process_pipeline': '',
                    'parent_folder_geid': 'c1c3766f-36bd-42db-8ca5-9040726cbc03-1620764271',
                    'name': 'test.zip',
                    'time_created': '2021-05-12T13:10:52',
                    'guid': '9fc4353b-c4d3-4d29-aa11-d04688f4abc7',
                    'full_path': '/data/storage/may511/raw/folders1/test.zip',
                    'dcm_id': 'undefined',
                }
            ],
        },
    )


def http_query_node(query_params={}):
    payload = {**query_params}
    node_query_url = ConfigClass.NEO4J_SERVICE_V1 + 'nodes/Container/query'
    with httpx.Client() as client:
        response = client.post(node_query_url, json=payload)
    return response
