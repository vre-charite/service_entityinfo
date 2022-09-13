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

def test_v1_get_system_metrics_return_200(test_client, create_db_system_metrics):
    response = test_client.get(f"v1/stats")
    assert response.status_code == 200


def test_v1_get_system_metrics_with_date_return_200(test_client, create_db_system_metrics):
    response = test_client.get(f"v1/stats?date='2022-02-09'")
    assert response.status_code == 200


def test_v1_get_system_metrics_with_invalid_date_return_500(test_client, create_db_system_metrics):
    response = test_client.get(f"v1/stats?date='2015-01-20'")
    res = response.json()
    assert response.status_code == 500
    assert res["error_msg"] == "Retrieval of metrics failed: Failure to query metrics from database table"
