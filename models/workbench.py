from pydantic import BaseModel, Field
from models.base_models import APIResponse, PaginationRequest


class GETWorkbenchResponse(APIResponse):
    result: dict = Field({}, example={
        'superset': {
          'deployed': True,
          'deployed_by': 'admin',
          'deployed_date': '2021-05-05T20:42:28.164241'
         },
        'guacamole': {
          'deployed': True,
          'deployed_by': 'admin',
          'deployed_date': '2021-05-05T20:42:28.164241'
         }
    })


class POSTWorkbenchResponse(APIResponse):
    result: str = Field("", example="success")

class POSTWorkbenchRequest(BaseModel):
    workbench_resource: str
    deployed: bool
    deployed_by: str
