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

project_geid = "abc123"


def test_v1_create_file_return_200(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json=[{"id": 300}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "pipeline",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    assert response.status_code == 200


def test_v1_create_file_elastic_search_fails_to_create_entry_return_500(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json=[{"id": 300}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=500,
        json={}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "pipeline",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    res = response.json()
    assert response.status_code == 500
    assert "Elastic Search Error" in res["error_msg"]


def test_v1_create_file_with_missing_field_operator_return_400(test_client):
    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "admin",
        "input_file_id": 5,
        "operator": "",
        "process_pipeline": "pipeline",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    res = response.json()
    print(res)
    assert res["error_msg"] == "Missing required field operator for input_file_id"
    assert response.status_code == 400


def test_v1_create_file_with_missing_process_pipeline_return_400(test_client):
    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "False",
        "input_file_id": 5,
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    res = response.json()
    assert res["error_msg"] == "Missing required field process_pipeline for input_file_id"
    assert response.status_code == 400


def test_v1_create_file_with_greenroom_namespace_return_200(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json=[{"id": 300}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "greenroom",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "pipeline",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    assert response.status_code == 200


def test_v1_create_file_with_failed_neo4j_node_file_query_return_500(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=500,
        json=[{}]
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "pipeline",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }

    response = test_client.post(f"/v1/files/", json=payload)
    res = response.json()
    assert response.status_code == 500
    assert "Neo4j error" in res["error_msg"]


def test_v1_create_file_with_failed_neo4j_relations_query_return_500(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json=[{"id": 300}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=500,
        json={}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "greenroom",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "pipeline",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    res = response.json()
    assert response.status_code == 500
    assert "Neo4j error" in res["error_msg"]


def test_v1_create_file_with_missing_parent_folder_geid_return_200(test_client, httpx_mock, mocker):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    mocker.patch("api.api_files.files.get_container_id", return_value=10)

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "pipeline",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "project_code": "testproject",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    assert response.status_code == 200


def test_v1_create_file_with_missing_parent_folder_geid_failed_neo4j_relation_query_return_500(test_client, httpx_mock,
                                                                                               mocker):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    mocker.patch("api.api_files.files.get_container_id", return_value=10)

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=500,
        json={}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "pipeline",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "project_code": "testproject",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    res = response.json()
    assert response.status_code == 500
    assert "Neo4j error" in res["error_msg"]


def test_v1_create_file_with_valid_input_file_id_return_200(test_client, httpx_mock):
    process_pipeline = "pipeline"

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json=[{"id": 300}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url=f"http://neo4j_service/v1/neo4j/relations/{process_pipeline}",
        status_code=200,
        json=[{"id": 100}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "",
        "input_file_id": 111,
        "process_pipeline": process_pipeline,
        "operator": "admin",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    assert response.status_code == 200


def test_v1_create_file_with_valid_input_file_id_neo4j_relations_fail_return_500(test_client, httpx_mock):
    process_pipeline = "pipeline"

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json=[{"id": 300}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url=f"http://neo4j_service/v1/neo4j/relations/{process_pipeline}",
        status_code=500,
        json=[{}]
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "",
        "input_file_id": 111,
        "process_pipeline": process_pipeline,
        "operator": "admin",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    res = response.json()
    assert response.status_code == 500
    assert "Neo4j error" in res["error_msg"]


def test_v1_create_file_where_process_pipeline_is_data_transfer_return_return_200(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File",
        status_code=200,
        json=[{"id": 100}]
    )

    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json=[{"id": 300}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        status_code=200,
        json=[{"manifest_id": 100, "full_path": "/full/path"}]
    )

    httpx_mock.add_response(
        method='GET',
        url="http://neo4j_service/v1/neo4j/manifest/100",
        status_code=200,
        json={"result": {
            "attributes": [{"name": "attr1", "value": "a1,a2,a3,a4,a5", "type": "multiple_choice", "optional": True}]}}
    )

    payload = {
        "file_size": 0,
        "full_path": "/path/to/file.pdf",
        "original_geid": "abc123",
        "dcm_id": "abcdefg123",
        "guid": "string",
        "namespace": "string",
        "uploader": "admin",
        "input_file_id": 0,
        "process_pipeline": "data_transfer",
        "operator": "",
        "tags": [],
        "global_entity_id": "",
        "parent_folder_geid": "abc1234",
        "project_code": "string",
        "location": "",
        "display_path": "",
        "version_id": ""
    }
    response = test_client.post(f"/v1/files/", json=payload)
    assert response.status_code == 200


def test_v1_query_file_by_container_project_geid_return_return_200(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.files.get_container_id", return_value=10)

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/query",
        status_code=200,
        json=[{"end_node": 1}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/query/count",
        status_code=200,
        json={"count": 4}
    )

    payload = {
        "page": 0,
        "page_size": 25,
        "order_type": "asc",
        "order_by": "time_created",
        "query": {
            "labels": [
                "File",
                "Folder"
            ],
            "File": {
                "name": "test",
                "partial": [
                    "name"
                ],
                "case_insensitive": [
                    "name"
                ]
            },
            "Folder": {
                "folder_name": "test"
            }
        }
    }
    response = test_client.post(f"/v1/files/{project_geid}/query", json=payload)
    assert response.status_code == 200


def test_v1_query_file_by_container_project_geid_with_invalid_order_type_return_return_400(test_client):
    payload = {
        "page": 0,
        "page_size": 25,
        "order_type": "invalidtype",
        "order_by": "time_created",
        "query": {
            "labels": [
                "File",
                "Folder"
            ],
            "File": {
                "name": "test",
                "partial": [
                    "name"
                ],
                "case_insensitive": [
                    "name"
                ]
            },
            "Folder": {
                "folder_name": "test"
            }
        }
    }
    response = test_client.post(f"/v1/files/{project_geid}/query", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert res["error_msg"] == "Invalid order_type"


def test_v1_query_file_by_container_project_geid_with_missing_attributes_return_return_400(test_client):
    payload = {
        "page": 0,
        "page_size": 25,
        "order_type": "asc",
        "order_by": "time_created",
        "query": {
            "labels": [
            ],
            "File": {
                "name": "test",
                "partial": [
                    "name"
                ],
                "case_insensitive": [
                    "name"
                ]
            },
            "Folder": {
                "folder_name": "test"
            }
        }
    }
    response = test_client.post(f"/v1/files/{project_geid}/query", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert res["error_msg"] == "Missing required attribute labels"


def test_v1_create_trash_file_return_200(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        status_code=200,
        json=[{"labels": [
            "Core",
            "File"
        ], "description": "test", "file_size": 500, "guid": "abc123", "manifest_id": "1",
            "dcm_id": "123", "uploader": "admin", "tags": "tag1", "id": 456, "global_entity_id": "bc45af32",
            "attr_1": "testvalue"}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/TrashFile",
        status_code=200,
        json=[{"id": 1010, "global_entity_id": "bc45af32"}]
    )

    global_entity_id = "bc45af32"
    httpx_mock.add_response(
        method='GET',
        url=f"http://neo4j_service/v1/neo4j/relations/connected/{global_entity_id}",
        status_code=200,
        json={
            "result": [
                {
                    "id": 4637,
                    "labels": [
                        "Greenroom",
                        "Container",
                        "Folder"
                    ],
                    "global_entity_id": "ebba4426-8b3a-11eb-8a88-eaff9e667817-1616437074",
                }]}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/deleted",
        status_code=200,
        json=[{"id": 1010}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json=[{"id": 1010}]
    )

    httpx_mock.add_response(
        method='PUT',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    payload = {
        "full_path": "/path/",
        "trash_full_path": "/trash/path",
        "trash_geid": "abc123",
        "geid": "abc12345"
    }
    response = test_client.post(f"/v1/files/trash", json=payload)
    assert response.status_code == 200


def test_v1_create_trash_file_by_full_path_return_200(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        status_code=200,
        json=[{"labels": [
            "Core",
            "File"
        ], "description": "test", "file_size": 500, "guid": "abc123", "manifest_id": "1",
            "dcm_id": "123", "uploader": "admin", "tags": "tag1", "id": 456, "global_entity_id": "bc45af32",
            "attr_1": "testvalue"}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/TrashFile",
        status_code=200,
        json=[{"id": 1010, "global_entity_id": "bc45af32"}]
    )

    global_entity_id = "bc45af32"
    httpx_mock.add_response(
        method='GET',
        url=f"http://neo4j_service/v1/neo4j/relations/connected/{global_entity_id}",
        status_code=200,
        json={
            "result": [
                {
                    "id": 4637,
                    "labels": [
                        "Greenroom",
                        "Container",
                        "Folder"
                    ],
                    "global_entity_id": "ebba4426-8b3a-11eb-8a88-eaff9e667817-1616437074",
                }]}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/deleted",
        status_code=200,
        json=[{"id": 1010}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json=[{"id": 1010}]
    )

    httpx_mock.add_response(
        method='PUT',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    payload = {
        "full_path": "/path/to/file",
        "trash_full_path": "/trash/path",
        "trash_geid": "abc123",
    }
    response = test_client.post(f"/v1/files/trash", json=payload)
    assert response.status_code == 200


def test_v1_create_trash_file_elastic_search_error_return_500(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/File/query",
        status_code=200,
        json=[{"labels": [
            "Core",
            "File"
        ], "description": "test", "file_size": 500, "guid": "abc123", "manifest_id": "1",
            "dcm_id": "123", "uploader": "admin", "tags": "tag1", "id": 456, "global_entity_id": "bc45af32"}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/TrashFile",
        status_code=200,
        json=[{"id": 1010, "global_entity_id": "bc45af32"}]
    )

    global_entity_id = "bc45af32"
    httpx_mock.add_response(
        method='GET',
        url=f"http://neo4j_service/v1/neo4j/relations/connected/{global_entity_id}",
        status_code=200,
        json={
            "result": [
                {
                    "id": 4637,
                    "labels": [
                        "Greenroom",
                        "Container",
                        "Folder"
                    ],
                    "global_entity_id": "ebba4426-8b3a-11eb-8a88-eaff9e667817-1616437074",
                }]}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/deleted",
        status_code=200,
        json=[{"id": 1010}]
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own",
        status_code=200,
        json=[{"id": 1010}]
    )

    httpx_mock.add_response(
        method='PUT',
        url="http://audit_trail_service/v1/entity/file",
        status_code=500,
        json={}
    )

    payload = {
        "full_path": "/path/",
        "trash_full_path": "/trash/path",
        "trash_geid": "abc123",
        "geid": "abc12345"
    }
    response = test_client.post(f"/v1/files/trash", json=payload)
    res = response.json()
    assert response.status_code == 500
    assert "Elastic Search Error" in res["error_msg"]


def test_v1_edit_attached_manifest_by_file_geid_return_200(test_client, httpx_mock, create_db_manifest, mocker):
    mocker.patch("api.api_files.files.get_file_node_bygeid", return_value={"manifest_id": 1, "id": 1,
                                                                           "global_entity_id": "j6127asb12"})

    httpx_mock.add_response(
        method='PUT',
        url="http://neo4j_service/v1/neo4j/nodes/File/node/1",
        status_code=200,
        json=[{}]
    )

    httpx_mock.add_response(
        method='PUT',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    file_geid = "abc123"
    payload = {"test123": "test"}
    response = test_client.put(f"/v1/files/{file_geid}/manifest", json=payload)
    res = response.json()
    assert response.status_code == 200


def test_v1_edit_attached_manifest_by_file_geid_elastic_search_fails_return_500(test_client, httpx_mock,
                                                                                create_db_manifest, mocker):
    mocker.patch("api.api_files.files.get_file_node_bygeid", return_value={"manifest_id": 1, "id": 1,
                                                                           "global_entity_id": "j6127asb12"})

    httpx_mock.add_response(
        method='PUT',
        url="http://neo4j_service/v1/neo4j/nodes/File/node/1",
        status_code=200,
        json=[{}]
    )

    httpx_mock.add_response(
        method='PUT',
        url="http://audit_trail_service/v1/entity/file",
        status_code=500,
        json={}
    )

    file_geid = "abc123"
    payload = {"test123": "test"}
    response = test_client.put(f"/v1/files/{file_geid}/manifest", json=payload)
    res = response.json()
    assert response.status_code == 500
    assert "Elastic Search Error" in res["error_msg"]


def test_v1_edit_attached_manifest_invalid_attribute_return_400(test_client, mocker, create_db_manifest, httpx_mock):
    mocker.patch("api.api_files.files.get_file_node_bygeid", return_value={"manifest_id": 3, "id": 1,
                                                                           "global_entity_id": "j6127asb12"})

    file_geid = "abc123"
    payload = {"test123": "test"}
    response = test_client.put(f"/v1/files/{file_geid}/manifest", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert "Not a valid attribute" in res["result"]


def test_v1_edit_attached_manifest_attribute_length_too_long_return_400(test_client, mocker, create_db_manifest,
                                                                        httpx_mock):
    mocker.patch("api.api_files.files.get_file_node_bygeid", return_value={"manifest_id": 1, "id": 1,
                                                                           "global_entity_id": "j6127asb12"})

    file_geid = "abc123"
    payload = {"test123": "test" * 120}
    response = test_client.put(f"/v1/files/{file_geid}/manifest", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert "text to long" in res["result"]


def test_v1_validate_input_to_attach_to_file_manifest_return_200(test_client, httpx_mock, create_db_manifest, mocker):
    mocker.patch('api.api_files.files.check_attributes', return_value=(True, ""))
    payload = {
        "manifest_name": "test123",
        "project_code": "testproject",
        "attributes": {"test123": "1"}
    }
    response = test_client.post(f"/v1/files/manifest/validate", json=payload)
    assert response.status_code == 200


def test_v1_validate_input_to_attach_to_file_manifest_with_invalid_attribute_return_400(test_client, httpx_mock,
                                                                                        create_db_manifest, mocker):
    mocker.patch('api.api_files.files.check_attributes', return_value=(True, ""))
    payload = {
        "manifest_name": "test123",
        "project_code": "testproject",
        "attributes": {"name": "attr1", "value": "a1,a2,a3,a4,a5", "type": "multiple_choice", "optional": False}
    }
    response = test_client.post(f"/v1/files/manifest/validate", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert "Invalid attribute" in res["result"]


def test_v1_validate_input_to_attach_to_file_manifest_with_invalid_manifest_404(test_client, httpx_mock,
                                                                                create_db_manifest, mocker):
    mocker.patch('api.api_files.files.check_attributes', return_value=(True, ""))
    payload = {
        "manifest_name": "test12345678",
        "project_code": "testproject",
        "attributes": {"test123": "1"}
    }
    response = test_client.post(f"/v1/files/manifest/validate", json=payload)
    res = response.json()
    assert response.status_code == 404
    assert "Manifest not found" in res["result"]


def test_v1_validate_input_to_attach_to_file_manifest_regex_attribute_check_failed_return_400(test_client, httpx_mock,
                                                                                              create_db_manifest,
                                                                                              mocker):
    mocker.patch('api.api_files.files.check_attributes', return_value=(False, "regex validation error"))
    payload = {
        "manifest_name": "test123",
        "project_code": "testproject",
        "attributes": {"test123": "1"}
    }
    response = test_client.post(f"/v1/files/manifest/validate", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert "regex validation error" in res["result"]


def test_v1_validate_input_to_attach_to_file_manifest_missing_required_attributes_return_400(test_client, httpx_mock,
                                                                                             create_db_manifest,
                                                                                             mocker):
    mocker.patch('api.api_files.files.check_attributes', return_value=(True, ""))
    mocker.patch('api.api_files.files.has_valid_attributes', return_value=(False, "Missing required attribute"))
    payload = {
        "manifest_name": "test123",
        "project_code": "testproject",
        "attributes": {"test123": "1"}
    }
    response = test_client.post(f"/v1/files/manifest/validate", json=payload)
    res = response.json()
    assert response.status_code == 400
    assert "Missing required attribute" in res["result"]
