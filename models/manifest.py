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


class GETManifestsResponse(APIResponse):
    result: list = Field([], example=[{
        'attributes': [{
            'id': 519,
            'manifest_id': 352,
            'name': 'attr1',
            'optional': True,
            'project_code': 'indoctestproject',
            'type': 'multiple_choice',
            'value': 'test,test2'
        }],
        'id': 352,
        'name': 'greg2',
        'project_code': 'indoctestproject'
    }])


class POSTManifestsResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': {   'id': 384,
                      'name': 'test222',
                      'project_code': 'indoctestproject'},
        'total': 1
    })


class POSTManifestsRequest(BaseModel):
    name: str
    project_code: str


class GETManifestResponse(APIResponse):
    result: dict = Field({}, example={
        'attributes': [{
            'id': 519,
            'manifest_id': 352,
            'name': 'attr1',
            'optional': True,
            'project_code': 'indoctestproject',
            'type': 'multiple_choice',
            'value': 'test,test2'
        }],
        'id': 352,
        'name': 'greg2',
        'project_code': 'indoctestproject'
    })


class PUTManifestRequest(BaseModel):
    name: str = ""


class PUTManifestResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': {   'id': 384,
                      'name': 'test222',
                      'project_code': 'indoctestproject'},
        'total': 1
    })

class DELETEManifestResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "success",
        'total': 1
    })


class POSTAttributesResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "success",
        'total': 1
    })

class POSTAttributesRequest(BaseModel):
    attributes: list

class PUTAttributeRequest(BaseModel):
    name: str = None 
    value: str = None 
    optional: bool = None 
    project_code: str = None
    type: str = None

class DELETEAttributeResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "success",
        'total': 1
    })

class POSTAttachResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "success",
        'total': 1
    })

class POSTAttachRequest(BaseModel):
    manifests: list

class PUTAttachResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "{}",
        'total': 1
    })

# class PUTAttachRequest(BaseModel):
#     payload: dict


class POSTValidateResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "Success",
        'total': 1
    })

class POSTValidateRequest(BaseModel):
    manifest_name: str
    project_code: str
    attributes: dict

class POSTImportRequest(BaseModel):
    name: str
    project_code: str
    attributes: list = [] 

class POSTImportResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "Success",
        'total': 1
    })

class GETExportResponse(BaseModel):
    result: dict = Field({}, example={})

class POSTQueryResponse(APIResponse):
    result: dict = Field({}, example={})

class POSTQueryRequest(APIResponse):
    geid_list: list
    lineage_view: bool = False 
