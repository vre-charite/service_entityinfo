from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from models import users as models
from models.base_models import APIResponse, EAPIResponseCode
from config import ConfigClass
import requests
import math

router = APIRouter()

@cbv(router)
class User:
    @router.get('/{username}', response_model=models.GETUserResponse, summary="Get User")
    async def get(self, username):
        api_response = APIResponse()
        response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/User/query", json={"name": username})
        if not response.json() or response.status_code == 404:
            api_response.error_msg = "User not found"
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        api_response.result = response.json()[0]
        return api_response.json_response()

    @router.put('/{username}', response_model=models.GETUserResponse, summary="update User")
    async def put(self, username, data: dict):
        api_response = APIResponse()
        response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/User/query", json={"name": username})
        if not response.json():
            api_response.error_msg = "User not found"
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        user_id = response.json()[0]["id"]
        response = requests.put(ConfigClass.NEO4J_SERVICE + f"nodes/User/node/{user_id}", json=data)
        api_response.result = response.json()
        return api_response.json_response()
