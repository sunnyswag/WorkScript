import os
import xml.etree.ElementTree as ET
import json
import re
import copy

PYTHON_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.split(PYTHON_FILE_DIR)[0]
RES_SUB_PATH = os.path.join("src", "main", "res")
COLOR_FILE = os.path.join("values", "colors.xml")

XML_COLOR_NODE_NAME = "color"
MODULE_CONFIG_FILE_NAME = "settings.gradle"
MODULE_TAG = "include"

def get_resource_collection(module_path: str) -> dict:
    result = {}
    res_path = os.path.join(module_path, RES_SUB_PATH)
    for dir_name in os.listdir(res_path):
        if os.path.isfile(os.path.join(res_path, dir_name)):
            continue

        if COLOR_FILE.startswith(dir_name):
            file_path = os.path.join(res_path, COLOR_FILE)
            result[COLOR_FILE] = [i.get("name") for i in ET.parse(file_path).getroot().findall(XML_COLOR_NODE_NAME)]
        else:
            file_path = os.path.join(res_path, dir_name)
            result[dir_name] = [i for i in os.listdir(file_path)]
    return result

def get_module_config_from_settings_gradle():
    result = {}
    with open(os.path.join(PROJECT_ROOT_DIR, MODULE_CONFIG_FILE_NAME), 'r', encoding='utf-8') as file:
        module_res = [re.search(r"include ':(.*?)'\n", i).group(1).replace(":", os.path.sep) for i in file.readlines() if i.startswith(MODULE_TAG)]
        all_module = list(filter(lambda i: "test" not in i, module_res))
        for i in all_module:
            cur_group_name = i.split(os.path.sep)[0]
            if cur_group_name not in result.keys():
                result[cur_group_name] = [i]
            else:
                result[cur_group_name].append(i)
        result["all"] = all_module
    return result

def save_to_json_file(filename, content):
    with open(os.path.join(PYTHON_FILE_DIR, filename), 'w', encoding="utf-8") as file:
        json.dump(content, file, indent=2)

def compose_all_modules(key, all_modules_data: dict) -> dict:
    result = copy.deepcopy(list(all_modules_data.values())[0])
    for content in list(all_modules_data.values())[1:]:
        for dir_name, data in content.items():
            for item in data:
                if item not in result[dir_name]:
                    result[dir_name].append(item)
    save_to_json_file("composed_{}_data.json".format(key), result)
    return result

def compare_each_module_with_composed_data(key: str, module_data_composed: dict, all_modules_data: dict):
    result = {}
    for module_name, content in all_modules_data.items():
        cur_module_missed_data = {}
        for cur_module_item, composed_module_item in zip(content.items(), module_data_composed.items()):
            missed_data = []
            for i in composed_module_item[1]:
                if i not in cur_module_item[1]:
                    missed_data.append(i)
            if missed_data:
                cur_module_missed_data[composed_module_item[0]] = missed_data
        if cur_module_missed_data:
            result[module_name] = cur_module_missed_data
    save_to_json_file("{}_missed_data_info.json".format(key), result)
    return result

def get_all_modules_data(modules):
    result = {}
    for module_name in modules:
        result[module_name] = get_resource_collection(os.path.join(PROJECT_ROOT_DIR, module_name))
    return result

if __name__ == "__main__":
    for key, modules in get_module_config_from_settings_gradle().items():
        all_modules_data = get_all_modules_data(modules)
        module_data_composed = compose_all_modules(key, all_modules_data)
        compare_each_module_with_composed_data(key, module_data_composed, all_modules_data)