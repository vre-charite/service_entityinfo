from pydantic import BaseModel, Field
from models.base_models import APIResponse, PaginationRequest


### CreateTrashPOST
class CreateTrashPOST(BaseModel):
    full_path: str
    trash_full_path: str
    trash_geid: str = ""


class CreateTrashPOSTResponse(APIResponse):
    result: dict = Field({}, example={   
                'archived': False,
                'file_size': 1024,
                'full_path': '/data/vre-storage/generate/raw/BCD-1234_file_2.aacn',
                'generate_id': 'BCD-1234_2',
                'guid': '5321880a-1a41-4bc8-a5d5-9767323205792',
                'id': 478,
                'labels': ['VRECore', 'TrashFile', 'Processed'],
                'name': 'BCD-1234_file_2.aacn',
                'namespace': 'core',
                'path': '/data/vre-storage/generate/raw',
                'process_pipeline': 'greg_testing',
                'time_created': '2021-01-06T18:02:55',
                'time_lastmodified': '2021-01-06T18:02:55',
                'type': 'processed',
                'uploader': 'admin',
                'operator': 'admin'
          }
      )


### CreateFilePOST
class CreateFilePOST(BaseModel):
    file_size: int 
    full_path: str
    generate_id: str
    guid: str
    namespace: str
    type: str
    uploader: str
    project_id: int 
    input_file_id: int = None
    process_pipeline: str = ""
    operator: str = ""
    tags: list = []
    global_entity_id: str = ""


class CreateFilePOSTResponse(APIResponse):
    result: dict = Field({}, example={   
                'archived': False,
                'file_size': 1024,
                'full_path': '/data/vre-storage/generate/raw/BCD-1234_file_2.aacn',
                'generate_id': 'BCD-1234_2',
                'guid': '5321880a-1a41-4bc8-a5d5-9767323205792',
                'id': 478,
                'labels': ['VRECore', 'File', 'Processed'],
                'name': 'BCD-1234_file_2.aacn',
                'namespace': 'core',
                'path': '/data/vre-storage/generate/raw',
                'process_pipeline': 'greg_testing',
                'time_created': '2021-01-06T18:02:55',
                'time_lastmodified': '2021-01-06T18:02:55',
                'type': 'processed',
                'uploader': 'admin',
                'operator': 'admin',
                'tags': ['greg','test']
          }
      )

### DatasetFileQueryPOSTResponse
class DatasetFileQueryPOST(PaginationRequest):
    partial: bool = False
    query: dict = Field({}, example={
        "archived": True,
        "description": "description",
        "file_size": 0,
        "full_path": "/data/vre-storage/tvb/raw/test_seeds",
        "generate_id": "string",
        "guid": "f1547da2-8372-4ae3-9e2b-17c80e97f113",
        "name": "testzy9.txt",
        "path": "test/zy",
        "time_created": "2021-01-08T17:09:51",
        "time_lastmodified": "2021-01-08T17:09:51",
        "uploader": "admin",
        "labels": [ 
          "File",
          "Greenroom",
          "Raw"
        ]
    })




class DatasetFileQueryPOSTResponse(APIResponse):
    result: dict = Field({}, example={
           'code': 200,
           'error_msg': '',
           'num_of_pages': 14,
           'page': 1,
           'result': [{   
               'archived': False,
               'description': 'description',
               'file_size': 0,
               'full_path': 'test/zy/testzy9.txt',
               'generate_id': '',
               'guid': 'f1547da2-8372-4ae3-9e2b-17c80e97f113',
               'id': 74,
               'labels': ['Raw', 'File', 'Greenroom'],
               'name': 'testzy9.txt',
               'path': 'test/zy',
               'time_created': '2021-01-08T17:09:51',
               'time_lastmodified': '2021-01-08T17:09:51',
               'uploader': 'testzy',
               'process_pipeline': 'test'
            }],
            'total': 67
        }
    )





