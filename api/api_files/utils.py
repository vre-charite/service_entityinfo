def get_source_label(source_type):
    return {
        "Project": "Dataset",
        "Folder": "Folder",
        "TrashFile": "Dataset",
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
        else:
            label_list.append(label + "TrashFile")
    else:
        label_list.append(label + "File")
        label_list.append(label + "Folder")
    return label_list

def convert_query(labels, query, partial):
    filter_fields = {
        "File": ["name", "uploader", "archived"],
        "Folder": ["name", "uploader", "folder_level"],
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
            elif key == "permissions_uploader":
                if label != "VRECore:TrashFile":
                    neo4j_query[label]["uploader"] = value
    return neo4j_query
