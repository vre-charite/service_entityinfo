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

project_code = "unittest_entity_info"

def test_v1_check_if_file_exists_in_greenroom_return_200(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/nodes/query",
        status_code=200,
        json={"result": [{"id": 64739, "labels": ["Greenroom", "File"],
                          "global_entity_id": "27b12869-ae56",
                          "input_file_id": "27b12869", "display_path": "admin/entity_info_test_1",
                          "project_code": "unittest_entity_info"}]}
    )

    data = {
        "zone": "greenroom",
        "file_relative_path": "admin/entity_info_test_1"
    }

    response = test_client.get(f"/v1/project/{project_code}/file/exist", params=data)
    assert response.status_code == 200
    res = response.json()
    assert len(res['result']) == 1


def test_v1_check_if_file_exists_in_core_return_200(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/nodes/query",
        status_code=200,
        json={"result": [{"id": 64740, "labels": ["Core", "File"],
                          "global_entity_id": "27b12854678",
                          "input_file_id": "279898ab", "display_path": "admin/entity_info_test_3",
                          "project_code": "unittest_entity_info"}]}
    )

    data = {
        "zone": "core",
        "file_relative_path": "admin/entity_info_test_3"
    }

    response = test_client.get(f"/v1/project/{project_code}/file/exist", params=data)
    assert response.status_code == 200
    res = response.json()
    assert len(res['result']) == 1


def test_v1_confirm_file_not_exist_in_zone_return_404(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/nodes/query",
        json={"result": []}
    )

    data = {
        "zone": "core",
        "file_relative_path": "admin/entity_info_test_3333"
    }
    response = test_client.get(f"/v1/project/{project_code}/file/exist", params=data)
    assert response.status_code == 404
    res = response.json()
    assert res["result"] == []
    assert res["error_msg"] == 'File not found'


def test_v1_check_file_in_non_existant_zone_return_400(test_client):
    zone = "fakezone"
    data = {
        "zone": zone,
        "file_relative_path": "admin/entity_info_test_1"
    }
    response = test_client.get(f"/v1/project/{project_code}/file/exist", params=data)
    assert response.status_code == 400
    res = response.json()
    assert res["error_msg"] == 'Invalid zone'
    assert res["result"] == {}


def test_v1_check_file_with_invalid_payload_return_500(test_client, httpx_mock):
    zone = "core"
    data = {
        "zone": zone,
        "file_relative_path": "admin/entity_info_test_1",
        "added": "test"
    }

    result = test_client.get(f"/v1/project/{project_code}/file/exist", params=data)
    assert result.status_code == 500
