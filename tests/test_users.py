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

username = "testuser"

def test_v1_get_user_details_with_valid_username_return_200(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/User/query",
        status_code=200,
        json=[{"id": 43139}]
    )

    response = test_client.get(f"v1/users/{username}")
    assert response.status_code == 200


def test_v1_get_user_details_with_invalid_username_return_404(test_client, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/User/query",
        status_code=404,
        json=[]
    )

    response = test_client.get(f"v1/users/{username}")
    res = response.json()
    assert response.status_code == 404
    assert res["error_msg"] == "User not found"


def test_v1_update_user_details_with_valid_username_return_200(test_client, httpx_mock):

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/User/query",
        status_code=200,
        json=[{"id": 43139}]
    )

    httpx_mock.add_response(
        method='PUT',
        url="http://neo4j_service/v1/neo4j/nodes/User/node/43139",
        status_code=200,
        json=[]
    )

    payload = {"status": "active"}
    response = test_client.put(f"/v1/users/{username}", json=payload)
    assert response.status_code == 200


def test_v1_update_user_details_with_invalid_username_return_404(test_client, httpx_mock):

    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/User/query",
        status_code=404,
        json=[]
    )

    payload = {"status": "active"}
    response = test_client.put(f"/v1/users/{username}", json=payload)
    res = response.json()
    assert response.status_code == 404
    assert res["error_msg"] == "User not found"
