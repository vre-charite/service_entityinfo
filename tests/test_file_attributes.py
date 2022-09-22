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

project_geid = "b38c26d0-1d51-44f1-9ab6-3175bd41ccc9-111111"


def test_v1_attach_attribute_to_file_return_200(request, test_client, httpx_mock, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    # get file node from neo4j based on geid:
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        status_code=200,
        json=[{
            "global_entity_id": project_geid,
            "manifest_id": 1,
            "name": "test123"

        }],

    )

    payload = {
        "project_role": "admin",
        "username": "admin",
        "project_code": project_code,
        "manifest_id": 1,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    assert result.status_code == 200


def test_v1_attach_attribute_to_file_invalid_attributes_return_400(request, test_client, httpx_mock, create_db_manifest,
                                                                   mocker):
    project_code = request.getfixturevalue('create_db_manifest')

    mocker.patch('api.api_attributes.file_attributes.has_valid_attributes',
                 return_value=(False, "Missing required attribute"))

    payload = {
        "project_role": "admin",
        "username": "admin",
        "project_code": project_code,
        "manifest_id": 1,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    res = result.json()
    assert result.status_code == 400
    assert res["error_msg"] == "Missing required attribute"


def test_v1_attach_attribute_to_file_node_does_not_exist_return_200(request, test_client, httpx_mock,
                                                                    create_db_manifest, mocker):
    project_code = request.getfixturevalue('create_db_manifest')

    # get file node from neo4j based on geid:
    mocker.patch('api.api_attributes.file_attributes.get_file_node_bygeid',
                 return_value=None)

    mocker.patch('api.api_attributes.file_attributes.get_folder_node_bygeid',
                 return_value=None)

    mocker.patch('api.api_attributes.file_attributes.get_files_recursive',
                 return_value=[{"id": 5, "manifest_id": "1", "name": "test123", "global_entity_id": "jasd7qhvc"}])

    payload = {
        "project_role": "admin",
        "username": "admin",
        "project_code": project_code,
        "manifest_id": 1,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    assert result.status_code == 200


def test_v1_attach_attribute_to_file_node_does_not_exist_file_search_empty_return_200(request, test_client, httpx_mock,
                                                                                      create_db_manifest, mocker):
    project_code = request.getfixturevalue('create_db_manifest')

    # get file node from neo4j based on geid:
    mocker.patch('api.api_attributes.file_attributes.get_file_node_bygeid',
                 return_value=None)

    mocker.patch('api.api_attributes.file_attributes.get_folder_node_bygeid',
                 return_value=None)

    mocker.patch('api.api_attributes.file_attributes.get_files_recursive',
                 return_value=[])

    payload = {
        "project_role": "admin",
        "username": "admin",
        "project_code": project_code,
        "manifest_id": 1,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    assert result.status_code == 200


def test_v1_attach_attribute_to_file_without_manifest_id_in_file_node_return_200(request, test_client, httpx_mock,
                                                                                 create_db_manifest, mocker):
    project_code = request.getfixturevalue('create_db_manifest')

    # get file node from neo4j based on geid:
    mocker.patch('api.api_attributes.file_attributes.get_file_node_bygeid',
                 return_value={"name": "test123", "global_entity_id": "abc1123def"})

    mocker.patch('api.api_attributes.file_attributes.attach_attributes',
                 return_value=True)

    payload = {
        "project_role": "admin",
        "username": "admin",
        "project_code": project_code,
        "manifest_id": 1,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    assert result.status_code == 200


def test_v1_attach_duplicate_attributes_return_terminated(request, test_client, httpx_mock, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    # get file node from neo4j based on geid:
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        status_code=200,
        json=[{
            "global_entity_id": project_geid,
            "manifest_id": 2,
            "name": "test1234"

        }],

    )

    payload = {
        "project_role": "admin",
        "username": "admin",
        "project_code": project_code,
        "manifest_id": 2,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "1"},
        "inherit": False
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    res = result.json()
    assert res["result"][0]["operation_status"] == "TERMINATED"
    assert res["result"][0]["error_type"] == "attributes_duplicate"


def test_v1_missing_project_code_in_payload_return_422(test_client, create_db_manifest):
    payload = {
        "project_role": "admin",
        "username": "admin",
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    assert result.status_code == 422


def test_v1_invalid_manifest_id_in_payload_return_400(test_client, create_db_manifest):
    payload = {
        "project_role": "admin",
        "username": "admin",
        "manifest_id": 3,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    assert result.status_code == 400


def test_v1_attach_attribute_to_file_node_not_found_return_None(request, test_client, httpx_mock, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    # get file node from neo4j based on geid:
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        json=None,

    )

    payload = {
        "project_role": "admin",
        "username": "admin",
        "project_code": project_code,
        "manifest_id": 1,
        "global_entity_id": [project_geid],
        "attributes": {"test1": "2"},
        "inherit": True
    }

    result = test_client.post(f"/v1/files/attributes/attach", json=payload)
    res = result.json()
    assert res["result"] == None


def test_v1_create_attributes_with_manifest_id_return_200(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    payload = {
        "attributes": [
            {
                "manifest_id": 1,
                "name": "test12344",
                "type": "text",
                "value": None,
                "optional": True,
                "project_code": project_code
            }
        ]
    }
    result = test_client.post(f"/v1/attributes", json=payload)
    assert result.status_code == 200


def test_v1_cannot_create_attributes_if_manifest_attached_to_files_return_403(request, test_client, httpx_mock,
                                                                              create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    # retrieve file count:
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query/count",
        status_code=200,
        json={"count": 3}

    )

    payload = {
        "attributes": [
            {
                "manifest_id": 1,
                "name": "test12344",
                "type": "text",
                "value": None,
                "optional": False,
                "project_code": project_code
            }
        ]
    }
    result = test_client.post(f"/v1/attributes", json=payload)
    assert result.status_code == 403


def test_v1_create_attribute_with_missing_missing_name_field_return_400(test_client):
    payload = {
        "attributes": [
            {
                "manifest_id": 1,
                "type": "text",
                "value": None,
                "optional": True,
                "project_code": "testproject"
            }
        ]
    }
    result = test_client.post(f"/v1/attributes", json=payload)
    assert result.status_code == 400


def test_v1_update_attribute_return_200(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    attribute_id = 1
    payload = {
        "name": "word",
        "value": "test123",
        "optional": True,
        "project_code": project_code,
        "type": None
    }
    result = test_client.put(f"/v1/attribute/{attribute_id}", json=payload)
    assert result.status_code == 200


def test_v1_update_attribute_with_invalid_type_return_400(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    attribute_id = 1
    payload = {
        "name": "test_attr",
        "value": None,
        "optional": True,
        "project_code": "jul23",
        "type": "text"
    }
    result = test_client.put(f"/v1/attribute/{attribute_id}", json=payload)
    assert result.status_code == 400


def test_v1_update_attribute_with_invalid_attribute_id_return_404(request, test_client, create_db_manifest):
    project_code = request.getfixturevalue('create_db_manifest')

    attribute_id = 100
    payload = {
        "name": "test_attr",
        "value": None,
        "optional": True,
        "project_code": project_code,
        "type": None
    }
    result = test_client.put(f"/v1/attribute/{attribute_id}", json=payload)
    assert result.status_code == 404


def test_v1_delete_attribute_using_attribute_id_return_200(test_client, create_db_manifest):
    attribute_id = 1
    result = test_client.delete(f"/v1/attribute/{attribute_id}")
    assert result.status_code == 200


def test_v1_delete_attribute_using_invalid_attribute_id_return_404(test_client, create_db_manifest):
    attribute_id = 500
    result = test_client.delete(f"/v1/attribute/{attribute_id}")
    res = result.json()
    assert result.status_code == 404
    assert res["error_msg"] == 'Attribute not found'
