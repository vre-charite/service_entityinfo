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

from pydantic import Field
from models.base_models import APIResponse

class StatsResponse(APIResponse):
    """
    System Metrics/Stats Response Class
    """
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "result":
            {
                "active_user": 20,
                "project": 20,
                "storage": 250,
                "vm": 30,
                "cores": 20,
                "ram": 80,
                "date": "2022-01-12"
            }
    }
                         )
