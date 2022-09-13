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
from models.folders import http_query_node


### DatasetFileQueryPOSTResponse
class MetaGET(PaginationRequest):
    source_type: str
    zone: str
    partial: str = ''
    query: str = ''


class MetaGETResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'code': 200,
            'error_msg': '',
            'num_of_pages': 14,
            'page': 1,
            'result': [
                {
                    'archived': False,
                    'description': 'description',
                    'file_size': 0,
                    'full_path': 'test/zy/testzy9.txt',
                    'dcm_id': '',
                    'guid': 'f1547da2-8372-4ae3-9e2b-17c80e97f113',
                    'id': 74,
                    'labels': ['Raw', 'File', 'Greenroom'],
                    'name': 'testzy9.txt',
                    'path': 'test/zy',
                    'time_created': '2021-01-08T17:09:51',
                    'time_lastmodified': '2021-01-08T17:09:51',
                    'uploader': 'testzy',
                    'process_pipeline': 'test',
                }
            ],
            'total': 67,
        },
    )


class POSTFileDetail(BaseModel):
    geids: list


class POSTFileDetailResponse(APIResponse):
    result: list = Field(
        {},
        example={
            'code': 200,
            'error_msg': '',
            'num_of_pages': 1,
            'page': 1,
            'result': [
                {
                    'archived': False,
                    'description': 'description',
                    'file_size': 0,
                    'full_path': 'test/zy/testzy9.txt',
                    'dcm_id': '',
                    'guid': 'f1547da2-8372-4ae3-9e2b-17c80e97f113',
                    'id': 74,
                    'labels': ['Raw', 'File', 'Greenroom'],
                    'name': 'testzy9.txt',
                    'path': 'test/zy',
                    'time_created': '2021-01-08T17:09:51',
                    'time_lastmodified': '2021-01-08T17:09:51',
                    'uploader': 'testzy',
                    'process_pipeline': 'test',
                }
            ],
            'total': 1,
        },
    )


class GETFileDetail(APIResponse):
    result: dict = Field(
        {},
        example={
            'code': 200,
            'error_msg': '',
            'num_of_pages': 1,
            'page': 1,
            'result': {
                'archived': False,
                'description': 'description',
                'file_size': 0,
                'full_path': 'test/zy/testzy9.txt',
                'dcm_id': '',
                'guid': 'f1547da2-8372-4ae3-9e2b-17c80e97f113',
                'id': 74,
                'labels': ['Raw', 'File', 'Greenroom'],
                'name': 'testzy9.txt',
                'path': 'test/zy',
                'time_created': '2021-01-08T17:09:51',
                'time_lastmodified': '2021-01-08T17:09:51',
                'uploader': 'testzy',
                'process_pipeline': 'test',
            },
            'total': 1,
        },
    )


def get_parent_connections(entity_geid):
    """get parent connections from neo4j service."""
    routing = []
    # get routing
    with httpx.Client() as client:
        response_routing = client.get(ConfigClass.NEO4J_SERVICE_V1 + 'relations/connected/{}'.format(entity_geid))
    routing = []
    if response_routing.status_code == 200:
        routing = response_routing.json()['result']
    else:
        raise (Exception('[v2 connected query] {}, {}'.format(response_routing.status_code, response_routing.text)))

    # add self node, if not returned by neo4j
    if len([route for route in routing if route['global_entity_id'] == entity_geid]) == 0:
        self_query_payload = {'global_entity_id': entity_geid}
        self_query_respon = http_query_node('doesnotmatterforgeidquery', self_query_payload)
        if self_query_respon.status_code == 200:
            routing = routing + self_query_respon.json()
        else:
            raise (Exception('[v2 routing query] {}, {}'.format(self_query_respon.status_code, self_query_respon.text)))

    return routing
