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

project_code = "unittest_entity_info_files_meta"
geid = "b38c26d0-1d51-44f1-9ab6-3175bd41ccc9-111111"


def test_v1_get_file_metadata_by_geid_return_200(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.meta.convert_query", return_value={})

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/relations/query",
        status_code=200,
        json={"total": 2, "results": [{"name": "entityinfo_unittest_folder",
                                       "project_code": "unittest_entity_info_files_meta"}]}

    )

    mocker.patch("api.api_files.meta.get_parent_connections", return_value={})

    payload = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{}',
        'source_type': 'Project',
        'zone': 'Greenroom',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=payload)
    assert result.status_code == 200
    res = result.json()
    res = res.get('result')
    meta_list = res.get('data')
    assert isinstance(res["data"], list) == True
    file = meta_list[0]
    assert file["name"] == "entityinfo_unittest_folder"


def test_v1_get_file_metadata_by_geid_neo4j_error_return_500(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.meta.convert_query", return_value={})

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/relations/query",
        status_code=500,
        json={}

    )

    payload = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{}',
        'source_type': 'Project',
        'zone': 'Greenroom',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=payload)
    assert result.status_code == 500
    res = result.json()
    assert "Neo4j error" in res["error_msg"]


def test_v1_get_files_pagination_return_200(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.meta.convert_query", return_value={})

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/relations/query",
        status_code=200,
        json={"total": 2, "results": [{"name": "entityinfo_unittest_folder",
                                       "project_code": "unittest_entity_info_files_meta"}]}

    )

    mocker.patch("api.api_files.meta.get_parent_connections", return_value={})

    data = {
        'page': 1,
        'page_size': 1,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{}',
        'source_type': 'Project',
        'zone': 'All',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 200
    res = result.json()
    res = res.get('result')
    meta_list = res.get('data')
    assert isinstance(meta_list, list) == True
    file = meta_list[0]
    assert file["project_code"] == "unittest_entity_info_files_meta"
    assert file["name"] == "entityinfo_unittest_folder"


def test_v1_get_single_file_from_query_return_200(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.meta.convert_query", return_value={})

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/relations/query",
        status_code=200,
        json={"total": 1, "results": [{"name": "entityinfo_unittest",
                                       "project_code": "unittest_entity_info_files_meta"}]}

    )

    mocker.patch("api.api_files.meta.get_parent_connections", return_value={})

    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{"name": "entity_info_meta_test_1"}',
        'source_type': 'Project',
        'zone': 'All',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 200
    res = result.json()
    assert res["total"] == 1
    res = res.get('result')
    meta_list = res.get('data')
    assert isinstance(meta_list, list) == True
    file = meta_list[0]
    assert file["project_code"] == "unittest_entity_info_files_meta"
    assert file["name"] == "entityinfo_unittest"


def test_v1_get_files_with_invalid_order_type_return_400(test_client):
    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc2',
        'query': '{"name": "entity_info_meta_test_1"}',
        'source_type': 'Project',
        'zone': 'All',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 400
    res = result.json()
    assert res["error_msg"] == "Invalid order_type"


def test_v1_get_files_with_missing_zone_return_422(test_client):
    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{"name": "entity_info_meta_test_1"}',
        'source_type': 'Project',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 422
    res = result.json()
    assert res["detail"][0]['msg'] == "field required"


def test_v1_get_folder_files_in_all_zones_return_200(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.meta.convert_query", return_value={})

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/relations/query",
        status_code=200,
        json={"total": 1, "results": [{"name": "entity_info_folder_file_meta_1",
                                       "project_code": "unittest_entity_info_files_meta"}]}

    )

    mocker.patch("api.api_files.meta.get_parent_connections", return_value={})

    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'source_type': 'Folder',
        'zone': 'All',
    }

    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 200
    res = result.json()
    res = res.get('result')
    meta_list = res.get('data')
    assert isinstance(meta_list, list) == True
    file = meta_list[0]
    assert file["project_code"] == "unittest_entity_info_files_meta"
    assert file["name"] == "entity_info_folder_file_meta_1"


def test_v1_get_folder_files_with_missing_source_type_return_422(test_client):
    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{"name": "entity_info_meta_test_1"}',
        'zone': 'All',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 422
    res = result.json()
    assert res["detail"][0]['msg'] == "field required"


def test_v1_get_folder_files_with_invalid_order_type_return_400(test_client):
    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc2',
        'query': '{"name": "entity_info_meta_test_1"}',
        'zone': 'All',
        'source_type': 'Folder',
    }
    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 400
    res = result.json()
    assert res["error_msg"] == "Invalid order_type"


def test_v1_get_folder_files_with_missing_query_return_400(test_client):
    folder_geid = "abc123"
    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
    }

    result = test_client.post(f"/v2/files/folder/{folder_geid}/query", json=data)
    assert result.status_code == 400
    res = result.json()
    assert res["error_msg"] == "Missing required attribute query"


def test_v1_get_folder_files_with_invalid_source_type_return_400(test_client):
    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{"name": "entity_info_meta_test_1"}',
        'zone': 'All',
        'source_type': 'bad',
    }

    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 400
    res = result.json()
    assert res["error_msg"] == "Invalid source_type"


def test_v1_get_folder_files_with_invalid_zone_return_400(test_client):
    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'query': '{"name": "entity_info_meta_test_1"}',
        'zone': 'bad',
        'source_type': 'Folder',
    }

    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 400
    res = result.json()
    assert res["error_msg"] == "Invalid zone"


def test_v1_get_folder_files_with_partial_parameter_return_200(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.meta.convert_query", return_value={"partial": "test"})

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/relations/query",
        status_code=200,
        json={"total": 3, "results": [{"name": "entity_info_folder_file_meta_1",
                                       "project_code": "unittest_entity_info_files_meta"}, "test1", "test2"]}

    )

    mocker.patch("api.api_files.meta.get_parent_connections", return_value={})

    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'source_type': 'Project',
        'query': '{"name": "entity_info_meta_test"}',
        'partial': '["name"]',
        'zone': 'All',
    }

    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 200
    res = result.json()
    res = res.get('result')
    meta_list = res.get('data')
    assert isinstance(meta_list, list) == True
    assert len(meta_list) == 3


def test_v1_get_folder_files_in_trash_return_200(test_client, httpx_mock, mocker):
    mocker.patch("api.api_files.meta.convert_query", return_value={})

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v2/neo4j/relations/query",
        status_code=200,
        json={"total": 0, "results": []}

    )

    mocker.patch("api.api_files.meta.get_parent_connections", return_value={})

    data = {
        'page': 0,
        'page_size': 10,
        'order_by': 'name',
        'order_type': 'desc',
        'source_type': 'TrashFile',
        'zone': 'All',
    }

    result = test_client.get(f"/v1/files/meta/{geid}", params=data)
    assert result.status_code == 200
    res = result.json()
    res = res.get('result')
    meta_list = res.get('data')
    assert isinstance(meta_list, list) == True
    assert len(meta_list) == 0


def test_v1_get_bulk_files_metadata_detail_return_200(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/query/geids",
        status_code=200,
        json={}

    )

    data = {"geids": ["abc123"]}
    result = test_client.post(f"/v1/files/bulk/detail", json=data)
    assert result.status_code == 200


def test_v1_get_bulk_files_metadata_detail_neo4j_error_return_500(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/query/geids",
        status_code=500,
        json={}

    )

    data = {"geids": ["abc123456"]}
    result = test_client.post(f"/v1/files/bulk/detail", json=data)
    res = result.json()
    assert result.status_code == 500
    assert "Neo4j error" in res["error_msg"]


def test_v1_get_bulk_files_metadata_detail_with_missing_geid_return_400(test_client):
    data = {"geids": []}
    result = test_client.post(f"/v1/files/bulk/detail", json=data)
    res = result.json()
    assert res["error_msg"] == "geids is required"
    assert result.status_code == 400


def test_v1_get_detail_of_single_file_by_geid_return_200(test_client, httpx_mock):
    file_geid = geid
    httpx_mock.add_response(
        method='GET',
        url=f"http://neo4j_service/v1/neo4j/nodes/geid/{file_geid}",
        status_code=200,
        json=[{"file1": "text"}]

    )
    result = test_client.get(f"v1/files/detail/{file_geid}")
    assert result.status_code == 200


def test_v1_get_detail_of_single_file_by_geid_file_neo4j_error_return_500(test_client, httpx_mock):
    file_geid = geid
    httpx_mock.add_response(
        method='GET',
        url=f"http://neo4j_service/v1/neo4j/nodes/geid/{file_geid}",
        status_code=404,
        json=""

    )
    result = test_client.get(f"v1/files/detail/{file_geid}")
    res = result.json()
    assert result.status_code == 500
    assert "Neo4j error" in res["error_msg"]


def test_v1_get_detail_of_single_file_by_geid_file_not_found_return_404(test_client, httpx_mock):
    file_geid = geid
    httpx_mock.add_response(
        method='GET',
        url=f"http://neo4j_service/v1/neo4j/nodes/geid/{file_geid}",
        status_code=200,
        json=False

    )
    result = test_client.get(f"v1/files/detail/{file_geid}")
    res = result.json()
    assert result.status_code == 404
    assert res["error_msg"] == "File not found"
