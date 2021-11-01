import requests
from config import ConfigClass
from models.manifest_sql import DataManifestModel , DataAttributeModel, TypeEnum
from fastapi_sqlalchemy import db
import re
import time


def get_files_recursive(folder_geid, all_files=[]):
    query = {
        "start_label": "Folder",
        "end_labels": ["File", "Folder"],
        "query": {
            "start_params": {
                "global_entity_id": folder_geid,
            },
            "end_params": {
                "archived": False
            }
        }
    }

    resp = requests.post(ConfigClass.NEO4J_SERVICE_V2 + "relations/query", json=query)
    for node in resp.json()["results"]:
        if "File" in node["labels"]:
            all_files.append(node)
        else:
            get_files_recursive(node["global_entity_id"], all_files=all_files)

    return all_files

# TODO remove the label checking by get by geid
def get_source_label(source_type):
    return {
        "Project": "Container",
        "Folder": "Folder",
        "TrashFile": "Container",
        "Collection": "VirtualFolder",
    }.get(source_type, "")


def get_query_labels(zone, source_type):
    if not zone in ["Greenroom", "VRECore", "All"]:
        return False

    label_list = []
    label = {
        "Greenroom": "Greenroom:",
        "VRECore": "VRECore:",
        "All": "",
    }.get(zone, "")
    if source_type == "TrashFile":
        if zone == "All":
            label_list.append("VRECore:TrashFile")
            label_list.append("Greenroom:TrashFile")
            label_list.append("VRECore:Folder")
            label_list.append("Greenroom:Folder")
        else:
            label_list.append(label + "TrashFile")
            label_list.append(label + "Folder")
    elif source_type == "Folder":
        label_list.append(label + "File")
        label_list.append(label + "Folder")
        label_list.append(label + "TrashFile")
    else:
        label_list.append(label + "File")
        label_list.append(label + "Folder")
    return label_list


def convert_query(labels, query, partial, source_type):
    filter_fields = {
        "File": ["name", "uploader", "archived"],
        "Folder": ["name", "uploader", "folder_level", "archived"],
        "TrashFile": ["name", "uploader", "archived"],
    }

    neo4j_query = {}
    for label in labels:
        neo4j_query[label] = {}
        allowed_fields = filter_fields[label.split(":")[-1]]
        for key, value in query.items():
            if key in allowed_fields:
                neo4j_query[label][key] = value
                if key in partial:
                    if not neo4j_query[label].get("partial"):
                        neo4j_query[label]["partial"] = []
                    neo4j_query[label]["partial"].append(key)
            elif key == "permissions_display_path":
                # here is for the user in collaborator role
                # the user can ONLY see their own file in greenroom
                # so we use the display path to do the authorization filter
                # in neo4j
                if label != "VRECore:TrashFile":
                    # add the ending slash for user who has same start(bug VRE-2046)
                    # eg. username1 vs username11
                    neo4j_query[label]["display_path"] = value + "/" 
                    neo4j_query[label]["startswith"] = ["display_path"] 
        if source_type == "TrashFile" and 'Folder' in label:
            neo4j_query[label]["in_trashbin"] = True
            if neo4j_query[label].get('archived'):
                del neo4j_query[label]['archived']

    return neo4j_query


def get_file_node_bygeid(geid):
    post_data = {"global_entity_id": geid}
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/File/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0]

def get_folder_node_bygeid(geid):
    post_data = {"global_entity_id": geid}
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/Folder/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0]

def get_trashfile_node_bygeid(geid):
    post_data = {"global_entity_id": geid}
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/TrashFile/query", json=post_data)
    if not response.json():
        return None
    return response.json()[0]

def get_file_node(full_path):
    post_data = {"full_path": full_path}
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/File/query", json=post_data)
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



def attach_attributes(manifest, attributes, file_node, _logger):
    post_data = {
        "manifest_id": manifest['id'],
    }

    sql_attributes = manifest['attributes']

    es_attributes = []

    for key in attributes:
        value = attributes[key]
        post_data["attr_" + key] = value

        sql_attribute = [x for x in sql_attributes if x['name'] == key]
        if len(sql_attribute) == 0:
            continue
        sql_attribute = sql_attribute[0]

        if sql_attribute["type"] == 'multiple_choice':
            attribute_value = []
            attribute_value.append(value)

            es_attributes.append({
                "attribute_name": key,
                "name": manifest['name'],
                "value": attribute_value
            })
        else:
            es_attributes.append({
                "attribute_name": key,
                "name": manifest['name'],
                "value": value
            })
    file_id = file_node["id"]
    response = requests.put(ConfigClass.NEO4J_SERVICE + f"nodes/File/node/{file_id}", json=post_data)

    if response.status_code != 200:
        _logger.error('Update Neo4j Node failed: {}'.format(response.text))
        return False

    # Update Elastic Search Entity
    es_payload = {
        "global_entity_id": file_node["global_entity_id"],
        "updated_fields": {
            "attributes": es_attributes,
            "time_lastmodified": time.time()
        }
    }
    es_res = requests.put(ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=es_payload)

    if es_res.status_code != 200:
        _logger.error('Update Elastic Search Entity failed: {}'.format(es_res.text))
        return False

    return True