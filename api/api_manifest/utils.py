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

import httpx
from config import ConfigClass
from models.manifest_sql import DataManifestModel , DataAttributeModel, TypeEnum
from fastapi_sqlalchemy import db
import re


def get_file_node_bygeid(geid):
    post_data = {"global_entity_id": geid}
    with httpx.Client() as client:
        response = client.post(ConfigClass.NEO4J_SERVICE_V1 + f"nodes/File/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0]


def get_folder_node_bygeid(geid):
    # imported but not used
    post_data = {"global_entity_id": geid}
    with httpx.Client() as client:
        response = client.post(ConfigClass.NEO4J_SERVICE_V1 + f"nodes/Folder/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0]


def get_trashfile_node_bygeid(geid):
    post_data = {"global_entity_id": geid}
    with httpx.Client() as client:
        response = client.post(ConfigClass.NEO4J_SERVICE_V1 + f"nodes/TrashFile/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0]


def get_file_node(full_path):
    post_data = {"full_path": full_path}
    with httpx.Client() as client:
        response = client.post(ConfigClass.NEO4J_SERVICE_V1 + f"nodes/File/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0]

def is_greenroom(file_node):
    if not "Greenroom" in file_node["labels"]:
        return False
    else:
        return True

def has_valid_attributes(manifest_id, data):
    attributes = db.session.query(DataAttributeModel).filter_by(manifest_id=manifest_id).order_by(DataAttributeModel.id.asc())
    for attr in attributes:
        if not attr.optional and not attr.name in data.get("attributes", {}):
            return False, "Missing required attribute"
        if attr.type.value == "multiple_choice":
            value = data.get("attributes", {}).get(attr.name)
            if value:
                if not value in attr.value.split(","):
                    return False, "Invalid choice field"
            else:
                if not attr.optional:
                    return False, "Field required"
        if attr.type.value == "text":
            value = data.get("attributes", {}).get(attr.name)
            if value:
                if len(value) > 100:
                    return False, "text to long"
            else:
                if not attr.optional:
                    return False, "Field required"
    return True, ""

def check_attributes(attributes):
    # Apply name restrictions
    name_requirements = re.compile("^[a-zA-z0-9]{1,32}$")
    for key, value in attributes.items():
        if not re.search(name_requirements, key):
            return False, "regex validation error"
    return True, ""
