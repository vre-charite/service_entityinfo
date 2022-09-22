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

def test_v1_get_file_daily_statistics_return_200(test_client, httpx_mock, mocker):
    project_geid = "abc123"
    # query node
    httpx_mock.add_response(
        method='POST',
        url="http://neo4j_service/v1/neo4j/nodes/Container/query",
        status_code=200,
        json=[{"code":200}]
    )

    mocker.patch('api.api_files.files_stats.get_operation_logs_total', return_value=[1, 2, 3, 4])
    mocker.patch('api.api_files.files_stats.get_file_count_neo4j', return_value=[1, 2, 3])

    response = test_client.get(
        f"/v1/project/{project_geid}/files/statistics?project_code=0401&start_date=1618200000&end_date=1618286399")
    assert response.status_code == 200
