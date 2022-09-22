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

def test_v1_get_folder_info_by_condition_return_200(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json={"result": [{"id": 100, "labels": ["Greenroom", "Folder"],
                          "global_entity_id": "27b12869-ae56"}]}
    )
    response = test_client.get(f"/v1/folders?zone=greenroom&project_code=testproject")
    assert response.status_code == 200


def test_v1_get_folder_info_with_invalid_zone_return_400(test_client, httpx_mock):
    # query node

    response = test_client.get(f"/v1/folders?zone=testzone&project_code=testproject")
    assert response.status_code == 400


def test_v1_get_folder_info_by_condition_with_folder_path_and_uploader_return_200(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=200,
        json={"result": [{"id": 100, "labels": ["Greenroom", "Folder"],
                          "global_entity_id": "27b12869-ae56"}]}
    )
    response = test_client.get(
        f"/v1/folders?zone=greenroom&project_code=testproject&folder_relative_path=/path/test&uploader=admin")
    assert response.status_code == 200


def test_v1_get_folder_info_by_condition_node_query_failed_return_500(test_client, httpx_mock):
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/query",
        status_code=500,
        json={}
    )
    response = test_client.get(f"/v1/folders?zone=greenroom&project_code=testproject")
    assert response.status_code == 500


def test_v1_create_folders_via_batch_return_200(test_client, httpx_mock):
    # bulk node create via neo4j
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/batch",
        status_code=200,
        json={}
    )

    # bulk create links in neo4j
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/relations/own/batch",
        status_code=200,
        json={}
    )

    payload = {
        "payload": [{
            "global_entity_id": "112345abcdefg123",
            "folder_name": "testfolder",
            "folder_level": 0,
            "folder_parent_geid": "112345abcdefg",
            "folder_parent_name": "parentfolder",
            "uploader": "admin",
            "folder_relative_path": "/test/path.pdf",
            "zone": "greenroom",
            "project_code": "testproject",
            "folder_tags": ["tag1"],
            "extra_labels": ["testlabel"],
            "extra_attrs": {"text": "attr"}
        }],
        "zone": "greenroom",
        "link_container": True}

    response = test_client.post(f"/v1/folders/batch", json=payload)
    assert response.status_code == 200


def test_v1_create_folders_via_batch_using_elastic_search_return_200(test_client, httpx_mock):
    # create folder in elastic search
    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json=""
    )

    # bulk node create via neo4j
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/batch",
        status_code=200,
        json={}
    )

    payload = {
        "payload": [{
            "global_entity_id": "112345abcdefg123",
            "folder_name": "testfolder",
            "folder_level": 0,
            "folder_parent_geid": "112345abcdefg",
            "folder_parent_name": False,
            "uploader": "admin",
            "folder_relative_path": "/test/path",
            "zone": "greenroom",
            "project_code": "testproject",
            "folder_tags": ["tag1"],
            "extra_labels": ["testlabel"],
            "extra_attrs": {"text": "attr"}
        }],
        "zone": "greenroom",
        "link_container": False}

    response = test_client.post(f"/v1/folders/batch", json=payload)
    assert response.status_code == 200


def test_v1_create_folders_via_batch_failed_elastic_search_return_500(test_client, httpx_mock):
    # create folder in elastic search
    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=500,
        json=""
    )

    payload = {
        "payload": [{
            "global_entity_id": "112345abcdefg123",
            "folder_name": "testfolder",
            "folder_level": 0,
            "folder_parent_geid": "112345abcdefg",
            "folder_parent_name": False,
            "uploader": "admin",
            "folder_relative_path": "/test/path",
            "zone": "greenroom",
            "project_code": "testproject",
            "folder_tags": ["tag1"],
            "extra_labels": ["testlabel"],
            "extra_attrs": {"text": "attr"}
        }],
        "zone": "greenroom",
        "link_container": False}

    response = test_client.post(f"/v1/folders/batch", json=payload)
    assert response.status_code == 500


def test_v1_creating_folders_via_batch_failed_relation_creation_raise_exception_returns_500(test_client, httpx_mock,
                                                                                            mocker):
    # bulk node create via neo4j
    mocker.patch('api.api_folders.folders.models.http_bulk_post_node')

    # bulk create links in neo4j
    mocker.patch('api.api_folders.folders.models.bulk_link_project',
                 side_effect=Exception("[bulk_link_project Error] {} {}".format(500, 'Error')))

    payload = {
        "payload": [{
            "global_entity_id": "112345abcdefg123",
            "folder_name": "testfolder",
            "folder_level": 0,
            "folder_parent_geid": "112345abcdefg",
            "folder_parent_name": "parentfolder",
            "uploader": "admin",
            "folder_relative_path": "/test/path.pdf",
            "zone": "greenroom",
            "project_code": "testproject",
            "folder_tags": ["tag1"],
            "extra_labels": ["testlabel"],
            "extra_attrs": {"text": "attr"}
        }],
        "zone": "greenroom",
        "link_container": True}

    response = test_client.post(f"/v1/folders/batch", json=payload)
    assert response.status_code == 500


def test_v1_creating_folders_via_batch_failed_relation_creation_returns_500(test_client, httpx_mock, mocker):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder/batch",
        status_code=200,
        json={}
    )

    # bulk create links in neo4j
    mocker.patch('api.api_folders.folders.models.bulk_link_project')
    mocker.patch.value = 500

    payload = {
        "payload": [{
            "global_entity_id": "112345abcdefg123",
            "folder_name": "testfolder",
            "folder_level": 0,
            "folder_parent_geid": "112345abcdefg",
            "folder_parent_name": "parentfolder",
            "uploader": "admin",
            "folder_relative_path": "/test/path.pdf",
            "zone": "greenroom",
            "project_code": "testproject",
            "folder_tags": ["tag1"],
            "extra_labels": ["testlabel"],
            "extra_attrs": {"text": "attr"}
        }],
        "zone": "greenroom",
        "link_container": True}

    response = test_client.post(f"/v1/folders/batch", json=payload)
    res = response.json()
    assert res["result"] == {"result": "failed to link projects with folders"}
    assert response.status_code == 500


def test_v1_creating_folders_via_batch_failed_node_query_returns_500(test_client, httpx_mock, mocker):
    mocker.patch('api.api_folders.folders.models.http_bulk_post_node')
    mocker.patch.value = 500

    payload = {
        "payload": [{
            "global_entity_id": "112345abcdefg123",
            "folder_name": "testfolder",
            "folder_level": 0,
            "folder_parent_geid": "112345abcdefg",
            "folder_parent_name": "parentfolder",
            "uploader": "admin",
            "folder_relative_path": "/test/path.pdf",
            "zone": "greenroom",
            "project_code": "testproject",
            "folder_tags": ["tag1"],
            "extra_labels": ["testlabel"],
            "extra_attrs": {"text": "attr"}
        }],
        "zone": "greenroom",
        "link_container": True}

    response = test_client.post(f"/v1/folders/batch", json=payload)
    assert response.status_code == 500


def test_v1_creating_folders_entity_return_200(test_client, httpx_mock, mocker):
    # create folder in elastic search
    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    # bulk node create via neo4j
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder",
        status_code=200,
        json=[{"global_entity_id": "1234"}]
    )

    mocker.patch('api.api_folders.folders.models.link_folder_parent')

    payload = {
        "global_entity_id": "112345abcdefg123",
        "folder_name": "testfolder",
        "folder_level": 0,
        "folder_parent_geid": "112345abcdefg",
        "folder_parent_name": "parentfolder",
        "uploader": "admin",
        "folder_relative_path": "/test/path.pdf",
        "project_code": "testproject",
        "folder_tags": ["tag1"],
        "extra_labels": ["testlabel"],
        "extra_attrs": {"text": "attr"},
        "zone": "greenroom",
        "link_container": True}

    response = test_client.post(f"/v1/folders", json=payload)
    assert response.status_code == 200


def test_v1_create_folders_failed_elastic_search_return_500(test_client, httpx_mock):
    # create folder in elastic search
    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=500,
        json=""
    )

    payload = {
        "global_entity_id": "112345abcdefg123",
        "folder_name": "testfolder",
        "folder_level": 0,
        "folder_parent_geid": "112345abcdefg",
        "folder_parent_name": "parentfolder",
        "uploader": "admin",
        "folder_relative_path": "/test/path.pdf",
        "project_code": "testproject",
        "folder_tags": ["tag1"],
        "extra_labels": ["testlabel"],
        "extra_attrs": {"text": "attr"},
        "zone": "greenroom",
        "link_container": True}

    response = test_client.post(f"/v1/folders", json=payload)
    assert response.status_code == 500


def test_v1_creating_folders_entity_with_trashbin_root_return_200(test_client, httpx_mock, mocker):
    # create folder in elastic search
    httpx_mock.add_response(
        method='POST',
        url="http://audit_trail_service/v1/entity/file",
        status_code=200,
        json={}
    )

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Folder",
        status_code=200,
        json=[{"global_entity_id": "1234"}]
    )

    mocker.patch('api.api_folders.folders.models.link_project')

    payload = {
        "global_entity_id": "112345abcdefg123",
        "folder_name": "testfolder",
        "folder_level": 0,
        "folder_parent_geid": "112345abcdefg",
        "folder_parent_name": "parentfolder",
        "uploader": "admin",
        "folder_relative_path": "/test/path.pdf",
        "project_code": "testproject",
        "folder_tags": ["tag1"],
        "extra_labels": ["testlabel"],
        "extra_attrs": {"text": "attr", "is_trashbin_root": "/root/path"},
        "zone": "greenroom",
        "link_container": True}

    response = test_client.post(f"/v1/folders", json=payload)
    assert response.status_code == 200
