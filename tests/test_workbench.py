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

import pytest
import os
from datetime import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from models.workbench_sql import Base as WorkbenchBase
from models.workbench_sql import WorkbenchModel
from sqlalchemy.future import create_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.schema import CreateSchema
from sqlalchemy import text

RDS_DB_URI = os.environ['RDS_DB_URI']
RDS_SCHEMA_DEFAULT = os.environ['RDS_SCHEMA_DEFAULT']
project_geid = "b38c26d0-1d51-44f1-9ab6-3175bd41ccc9-111111"

@pytest.fixture(autouse=True)
def create_db_workbench(db):
    engine = create_engine(db.get_connection_url())
    with engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {RDS_SCHEMA_DEFAULT};"))
    CreateTable(WorkbenchModel.__table__).compile(dialect=postgresql.dialect())
    WorkbenchBase.metadata.create_all(bind=engine)
    s = Session(engine)
    s.add(WorkbenchModel(geid=project_geid, project_code="testproject",
                         workbench_resource="superset", deployed=True, deployed_date=datetime.now(),
                         deployed_by="admin"))
    s.commit()
    yield
    WorkbenchBase.metadata.drop_all(bind=engine)


def test_v1_create_workbench_entry_with_jupyterhub_resource_return_200(test_client, httpx_mock):
    # get dataset node with project_geid
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Container/query",
        status_code=200,
        json=[{"code": "testproject"}]

    )
    data = {
        'workbench_resource': 'jupyterhub',
        'deployed': True,
        'deployed_by': 'admin',
    }
    result = test_client.post(f'/v1/{project_geid}/workbench', json=data)
    assert result.status_code == 200
    res = result.json()
    assert res['result'] == 'success'

def test_v1_create_workbench_entry_with_guacamole_resource_return_200(test_client, httpx_mock):
    # get dataset node with project_geid
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Container/query",
        status_code=200,
        json=[{"code": "testproject"}]

    )

    data = {
        'workbench_resource': 'guacamole',
        'deployed': True,
        'deployed_by': 'admin',
    }
    result = test_client.post(f"/v1/{project_geid}/workbench", json=data)
    assert result.status_code == 200
    res = result.json()
    assert res['result'] == 'success'


def test_v1_create_workbench_entry_with_invalid_geid_return_404(test_client, httpx_mock):
    project_geid = "invalidgeid"


    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Container/query",
        status_code=404,
        json=[{"code": ""}]

    )

    data = {
        'workbench_resource': 'guacamole',
        'deployed': True,
        'deployed_by': 'admin',
    }

    result = test_client.post(f"/v1/{project_geid}/workbench", json=data)
    assert result.status_code == 404


def test_v1_create_workbench_entry_with_invalid_resource_return_400(test_client):
    data = {
        'workbench_resource': 'resource1234',
        'deployed': True,
        'deployed_by': 'admin',
    }

    result = test_client.post(f"/v1/{project_geid}/workbench", json=data)
    assert result.status_code == 400
    res = result.json()
    assert res['error_msg'] == "Invalid workbench resource"


def test_v1_create_entry_with_missing_workbench_field_in_payload_return_422(test_client):
    data = {
        'deployed': True,
        'deployed_by': 'admin',
    }

    result = test_client.post(f"/v1/{project_geid}/workbench", json=data)
    assert result.status_code == 422


def test_v1_create_duplicate_entry_with_same_geid_and_workbench_return_500(test_client):
    data = {
        'workbench_resource': 'superset',
        'deployed': True,
        'deployed_by': 'admin',
    }

    result = test_client.post(f"/v1/{project_geid}/workbench", json=data)
    print(result.text)
    assert result.status_code == 500
    res = result.json()
    assert "Record already exists for this project and resource" in res["error_msg"]


def test_v1_get_workbench_entries_with_geid_return_200(test_client):
    result = test_client.get(f"/v1/{project_geid}/workbench")
    assert result.status_code == 200
    res = result.json()
    assert res["result"]["superset"]["deployed"] == True
    assert res["result"]["superset"]["deployed_by"] == "admin"


def test_v1_delete_workbench_entry_with_geid_return_200(test_client):
    id = 1
    result = test_client.delete(f"/v1/{project_geid}/workbench/{id}")
    assert result.status_code == 200


def test_v1_entry_not_found_when_delete_workbench_entry_with_geid_return_404(test_client):
    id = 2
    result = test_client.delete(f"/v1/{project_geid}/workbench/{id}")
    assert result.status_code == 404

