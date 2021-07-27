from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from fastapi_sqlalchemy import db
from models import workbench
from models.workbench_sql import WorkbenchModel
from models.base_models import APIResponse, EAPIResponseCode
from datetime import datetime
import requests
from config import ConfigClass

router = APIRouter()


@cbv(router)
class Workbench:
    @router.get('/{project_geid}/workbench', response_model=workbench.GETWorkbenchResponse, summary="Get workbench entry")
    async def get(self, project_geid):
        api_response = APIResponse()
        query_data = {
            "geid": project_geid,
        }
        try:
            workbench_objects = db.session.query(WorkbenchModel).filter_by(**query_data)
        except Exception as e:
            api_response.error_msg = "Error querying psql: " + str(e)
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()

        results = {} 
        for obj in workbench_objects:
            results[obj.workbench_resource] = {
                "deployed": obj.deployed,
                "deployed_date": obj.deployed_date.isoformat(),
                "deployed_by": obj.deployed_by,
                "id": obj.id,
            }
        api_response.total = workbench_objects.count()
        api_response.result = results
        return api_response.json_response()

    @router.post('/{project_geid}/workbench', response_model=workbench.POSTWorkbenchResponse, summary="Create a workbench entry")
    async def post(self, project_geid, data: workbench.POSTWorkbenchRequest):
        api_response = APIResponse()
        if not data.workbench_resource in ["guacamole", "superset", "jupyterhub"]:
            api_response.error_msg = "Invalid workbench resource"
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()

        # Duplicate check
        try:
            query = {
                "workbench_resource": data.workbench_resource, 
                "geid": project_geid, 
            }
            workbench_objects = db.session.query(WorkbenchModel).filter_by(**query)
            if workbench_objects.count() > 0:
                api_response.error_msg = "Record already exists for this project and resource"
                api_response.code = EAPIResponseCode.conflict
                return api_response.json_response()
        except Exception as e:
            api_response.error_msg = "Error querying psql: " + str(e)
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()

        response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/Container/query", json={"global_entity_id": project_geid})
        if response.status_code != 200:
            api_response.error_msg = response.json()
            api_response.code = response.status_code
            return api_response.json_response()
        dataset_node = response.json()[0]

        deployed_date = None
        if data.deployed:
            deployed_date = datetime.utcnow()
        deployed_by = ""
        if data.deployed:
            deployed_by = data.deployed_by

        sql_params = {
            "geid": project_geid,
            "project_code": dataset_node["code"],
            "workbench_resource": data.workbench_resource,
            "deployed": data.deployed,
            "deployed_date": deployed_date,
            "deployed_by": data.deployed_by,
        }
        try:
            workbench_object = WorkbenchModel(**sql_params)
            db.session.add(workbench_object)
            db.session.commit()
        except Exception as e:
            api_response.error_msg = "Error creating entry in psql: " + str(e)
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
        api_response.result = "success"
        return api_response.json_response()

    @router.delete('/{project_geid}/workbench/{id}', response_model=workbench.POSTWorkbenchResponse, summary="Delete a workbench entry")
    async def delete(self, project_geid, id):
        api_response = APIResponse()
        query = {
            "geid": project_geid, 
            "id": id, 
        }
        workbench_object = db.session.query(WorkbenchModel).filter_by(**query).first()
        if not workbench_object:
            api_response.error_msg = "Entry not found"
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        db.session.delete(workbench_object)
        db.session.commit()
        api_response.result = "success"
        return api_response.json_response()
