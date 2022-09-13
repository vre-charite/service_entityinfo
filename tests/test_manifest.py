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

import json
manifest_id = 1


def test_v1_create_manifest_return_200(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')
    data = {
        'name': 'unittest_manifest2',
        'project_code': project_code,
    }
    response = test_client.post(f"/v1/manifests", json=data)
    assert response.status_code == 200
    res = response.json()
    assert res["result"]["name"] == "unittest_manifest2"


def test_v1_get_manifest_name_with_manifest_id_return_200(test_client, create_db_manifest):
    response = test_client.get(f"/v1/manifest/{manifest_id}")
    assert response.status_code == 200
    res = response.json()
    assert res["result"]["name"] == "test123"


def test_v1_update_manifest_name_with_manifest_id_return_200(test_client, create_db_manifest):
    payload = {
        "name": "unittest_manifest",
    }
    response = test_client.put(f"/v1/manifest/{manifest_id}", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["result"]["name"] == "unittest_manifest"


def test_v1_export_manifest_with_respective_attributes_return_200(test_client, create_db_manifest):
    payload = {
        "manifest_id": manifest_id,
    }
    response = test_client.get(f"/v1/manifest/file/export", params=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["name"] == "test123"


def test_v1_import_new_manifest_return_200(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')
    payload = {
        "project_code": project_code,
        "name": "unit_test"
    }
    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["result"] == "Success"


def test_v1_import_new_manifest_attribute_validation_failed_return_400(request, test_client, create_db_manifest,
                                                                       mocker):
    mocker.patch('api.api_manifest.routes.check_attributes',
                 return_value=(False, "regex validation error"))

    project_code = request.getfixturevalue('create_db_manifest')
    payload = {
        "project_code": project_code,
        "name": "unit_test"
    }
    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert res["result"] == "regex validation error"


def test_v1_import_new_manifest_multiple_choice_validation_failed_return_400(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')
    payload = {
        "project_code": project_code,
        "name": "unit_test",
        "attributes": [{"name": "attr1", "value": "a1,a1,Ç3", "type": "multiple_choice", "optional": False}]
    }
    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert res["result"] == "regex value error"


def test_v1_import_new_manifest_with_attribute_too_long_return_400(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')
    payload = {
        "project_code": project_code,
        "name": "unit_test",
        "attributes": [{"name": "attr1", "value": "a1" * 120, "type": "text", "optional": False}]
    }
    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert res["result"] == "text to long"


def test_v1_delete_existing_manifest_return_200(test_client, create_db_manifest, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query/count",
        json={"count": 0}
    )

    response = test_client.delete(f"/v1/manifest/{manifest_id}")
    assert response.status_code == 200
    res = response.json()
    assert res["result"] == "success"


def test_v1_get_manifest_by_geid_query_return_200(test_client, create_db_manifest, httpx_mock):
    # get dataset node with project_geid
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        status_code=200,
        json=[{"code": "testproject", "manifest_id": 1}]

    )

    payload = {
        "geid_list": ["b38c26d0-1d51-44f1-9ab6-3175bd41ccc9-111111"],
    }
    response = test_client.post(f"/v1/manifest/query", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert len(res["result"]) == 1


def test_v1_get_manifest_list_with_missing_project_code_return_422(test_client):
    response = test_client.get(f"/v1/manifests")
    res = response.json()
    assert response.status_code == 422
    assert res["detail"][0]["msg"] == "field required"


def test_v1_create_duplicate_manifest_return_400(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')
    data = {
        'name': 'test123',
        'project_code': project_code,
    }
    response = test_client.post(f"/v1/manifests", json=data)
    assert response.status_code == 400
    res = response.json()
    assert res["result"] == "duplicate manifest name"


def test_v1_get_manifest_by_manifest_id_that_does_not_exist_return_404(test_client, create_db_manifest):
    manifest_id = 200
    result = test_client.get(f"/v1/manifest/{manifest_id}")
    assert result.status_code == 404
    res = result.json()
    assert res["error_msg"] == "Manifest not found"


def test_v1_update_manifest_by_manifest_id_that_does_not_exist_return_404(test_client, create_db_manifest):
    manifest_id = 200
    payload = {
        "name": "unittest_manifest3",
    }
    response = test_client.put(f"/v1/manifest/{manifest_id}", json=payload)
    assert response.status_code == 404
    res = response.json()
    assert res["error_msg"] == "Manifest not found"


def test_v1_delete_manifest_by_manifest_id_that_does_not_exist_return_404(test_client, create_db_manifest):
    manifest_id = 200
    response = test_client.delete(f"/v1/manifest/{manifest_id}")
    assert response.status_code == 404
    res = response.json()
    assert res["error_msg"] == "Manifest not found"


def test_v1_cannot_delete_manifest_due_to_multiple_linked_files_return_403(test_client, create_db_manifest, httpx_mock):

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query/count",
        status_code=200,
        json={"count": 5}

    )

    manifest_id = 1
    response = test_client.delete(f"/v1/manifest/{manifest_id}")
    assert response.status_code == 403
    res = response.json()
    assert res["result"] == "Can't delete manifest attached to files"

def test_v1_import_manifest_attributes_from_file_return_200(test_client, create_db_manifest, httpx_mock):

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query/count",
        status_code=200,
        json={"count": 0}

    )

    # insert attributes
    with open("tests/import_test.json", 'r') as f:
        payload = json.loads(f.read())
    payload["name"] = "unittest_manifest5"
    payload["project_code"] = "testproject2"

    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["result"] == "Success"

    # get imported manifest
    payload = {
        "project_code": "testproject2",
    }
    response = test_client.get(f"/v1/manifests", params=payload)
    res = response.json()["result"]
    assert response.status_code == 200
    res_values = res[0].values()
    assert "unittest_manifest5" in res_values


def test_v1_import_duplicate_manifest_from_file_return_400(test_client, create_db_manifest, httpx_mock):

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query/count",
        status_code=200,
        json={"count": 0}

    )
    # insert attributes
    with open("tests/import_test.json", 'r') as f:
        payload = json.loads(f.read())
    payload["name"] = "unittest_manifest5"
    payload["project_code"] = "testproject2"

    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["result"] == "Success"

    # insert same manifest again (duplicate)

    with open("tests/import_test.json", 'r') as f:
        payload = json.loads(f.read())
    payload["name"] = "unittest_manifest5"
    payload["project_code"] = "testproject2"

    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 400
    res = response.json()
    assert res["result"] == "duplicate manifest name"


def test_v1_import_duplicate_attribute_from_file_return_400(test_client, create_db_manifest, httpx_mock):

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query/count",
        status_code=200,
        json={"count": 0}

    )

    # insert attributes
    with open("tests/import_test.json", 'r') as f:
        payload = json.loads(f.read())
    payload["name"] = "unittest_manifest5"
    payload["project_code"] = "testproject2"

    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["result"] == "Success"

    # insert same attributes again (duplicate)
    with open("tests/import_test.json", 'r') as f:
        payload = json.loads(f.read())
    payload["name"] = "unittest_manifest6"
    payload["project_code"] = "testproject2"
    payload["attributes"].append({"name": "attr1"})

    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 400
    res = response.json()
    assert res["result"] == "duplicate attribute"


def test_v1_cannot_create_manifest_due_to_multiple_linked_files_return_403(test_client, create_db_manifest, httpx_mock):
    # get dataset node with project_geid
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query/count",
        status_code=200,
        json={"count": 5}

    )
    payload = {
        "project_code": "testproject",
        "name":"unittest_manifest15",
        "attributes": [{"name": "attr10", "value": "a1", "type": "text", "optional": False}]
    }
    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 403
    res = response.json()
    assert res["result"] == "Can't add required attributes to manifest attached to files"


def test_v1_cannot_create_manifest_due_to_missing_attribute_key_return_400(test_client, create_db_manifest, httpx_mock):
    payload = {
        "project_code": "testproject",
        "name":"unittest_manifest15",
        "attributes": [{"name": "attr10", "value": "a1", "type": "text"}]
    }
    response = test_client.post(f"/v1/manifest/file/import", json=payload)
    assert response.status_code == 400
    res = response.json()
    assert res["result"] == f"Missing required field optional"
