from pydantic import BaseModel, Field
from models.base_models import APIResponse, PaginationRequest


class GETUserResponse(BaseModel):
    result: dict = Field({}, example={})
