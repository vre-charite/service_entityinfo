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

from pydantic import BaseModel
from pydantic import Field

from config import ConfigClass
from models.base_models import APIResponse
from models.base_models import PaginationRequest


# CreateTrashPOST
class CreateTrashPOST(BaseModel):
    full_path: str
    trash_full_path: str
    trash_geid: str = ''
    geid: str = ''


class CreateTrashPOSTResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'archived': False,
            'file_size': 1024,
            'full_path': '/data/storage/service/raw/BCD-1234_file_2.aacn',
            'dcm_id': 'BCD-1234_2',
            'guid': '5321880a-1a41-4bc8-a5d5-9767323205792',
            'id': 478,
            'labels': ['Core', 'TrashFile', 'Processed'],
            'name': 'BCD-1234_file_2.aacn',
            'namespace': 'core',
            'path': '/data/storage/service/raw',
            'process_pipeline': 'greg_testing',
            'time_created': '2021-01-06T18:02:55',
            'time_lastmodified': '2021-01-06T18:02:55',
            'type': 'processed',
            'uploader': 'admin',
            'operator': 'admin',
        },
    )


# CreateFilePOST
class CreateFilePOST(BaseModel):
    file_size: int
    full_path: str
    original_geid: str = None
    dcm_id: str
    guid: str
    namespace: str
    uploader: str
    # project_id: int
    input_file_id: int = None
    process_pipeline: str = ''
    operator: str = ''
    tags: list = []
    global_entity_id: str = ''
    parent_folder_geid: str = None
    project_code: str
    # Minio attribute
    location: str = ''
    display_path: str = ''
    version_id: str = ''


class CreateFilePOSTResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'archived': False,
            'file_size': 1024,
            'display_path': '/data/storage/service/raw/BCD-1234_file_2.aacn',
            'dcm_id': 'BCD-1234_2',
            'guid': '5321880a-1a41-4bc8-a5d5-9767323205792',
            'id': 478,
            'labels': ['Core', 'File', 'Processed'],
            'name': 'BCD-1234_file_2.aacn',
            'namespace': 'core',
            'location': '/data/storage/service/raw',
            'process_pipeline': 'greg_testing',
            'time_created': '2021-01-06T18:02:55',
            'time_lastmodified': '2021-01-06T18:02:55',
            'type': 'processed',
            'uploader': 'admin',
            'operator': 'admin',
            'tags': ['greg', 'test'],
        },
    )


# DatasetFileQueryPOSTResponse


class DatasetFileQueryPOST(PaginationRequest):
    partial: bool = False
    query: dict = Field(
        {},
        example={
            'archived': True,
            'description': 'description',
            'file_size': 0,
            'full_path': '/data/storage/any/raw/test_seeds',
            'dcm_id': 'string',
            'guid': 'f1547da2-8372-4ae3-9e2b-17c80e97f113',
            'name': 'testzy9.txt',
            'path': 'test/zy',
            'time_created': '2021-01-08T17:09:51',
            'time_lastmodified': '2021-01-08T17:09:51',
            'uploader': 'admin',
            'labels': ['File', 'Greenroom', 'Raw'],
        },
    )


class DatasetFileQueryPOSTV2(PaginationRequest):
    query: dict = Field(
        {},
        example={
            'labels': ['File', 'Folder'],
            'File': {
                'name': 'test',
                'partial': ['name'],
                'case_insensitive': ['name'],
            },
            'Folder': {
                'folder_name': 'test',
            },
        },
    )


class DatasetFileQueryPOSTResponse(APIResponse):
    result: dict = Field(
        {},
        example=[
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
    )


class FilesStatsGETResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'uploaded': 0,
            'downloaded': 0,
            'approved': 0,  # get from neo4j
            # get from neo4j(archived: False), all files in greenroom
            'greenroom': 0,
            'core': 0,  # get from neo4j(archived: False), all files in core
        },
    )
