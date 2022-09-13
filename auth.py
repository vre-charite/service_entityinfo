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

import httpx
import jwt as pyjwt
from fastapi import Request
from logger import LoggerFactory

from config import ConfigClass

logger = LoggerFactory(__name__).get_logger()


def jwt_required(request: Request):
    """
        why is there no call to this function?!
        delete candidate!
    """
    token = request.headers.get('Authorization')
    if token:
        token = token.replace("Bearer ", "")
    else:
        raise Exception("Token required")
    payload = pyjwt.decode(token, verify=False)
    username: str = payload.get("preferred_username")

    # check if user is existed in neo4j
    url = ConfigClass.NEO4J_SERVICE_V1 + "nodes/User/query"
    with httpx.Client() as client:
        res = client.post(
            url,
            json={"name": username}
        )
    try:
        res.raise_for_status()
        if res.status_code != 200:
            raise Exception("Neo4j service: " + json.loads(res.text))
    except httpx.HTTPError as exc:
        logger.error("HTTP Exception", exc_info=True)
        raise exc

    users = res.json()
    if not users:
        raise Exception(f"Neo4j service: User {username} does not exist.")
    user_id = users[0]['id']
    role = users[0]['role']
    if username is None:
        raise Exception("User not found")
    return {"user_id": user_id, "username": username, "role": role}
