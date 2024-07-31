import sys
import os
import xml.etree.ElementTree as ET

# for example:
# python3 script/move_string_between_module.py module_panel:panel_network_error music:music_network_error

def check_user_input(source: str, destination: str):
    def raise_error(input: str, index_str: str):
        raise RuntimeError(f"input: {input}, {index_str} input format error!")

    if len(source.split(":")) != 2 or any([item == "" for item in source.split(":")]):
        raise_error(source, "source")

    if len(destination.split(":")) != 2 or all([item == "" for item in destination.split(":")]):
        raise_error(destination, "destination")

def get_user_input(source: str, destination: str):
    source_sub = source.split(":")
    source_module, source_str_id = source_sub[0], source_sub[1]

    destination_sub = destination.split(":")
    destination_module = source_module if destination_sub[0] == "" else destination_sub[0]
    destination_str_id = source_str_id if destination_sub[1] == "" else destination_sub[1]

    return source_module, source_str_id, destination_module, destination_str_id

def get_dir_path(module_name):
    for dirpath, dirnames, _ in os.walk(os.curdir):
        if module_name in dirnames:
            return os.path.join(dirpath, module_name, "src", "main", "res")

def update_source_file_and_get_str(source_module_path, dir_name):
    file_dir = os.path.join(source_module_path, dir_name, "strings.xml")
    cur_xml_source: ET.ElementTree = ET.parse(file_dir)
    for item in cur_xml_source.getroot().findall('string'):
        if item.get('name') == source_str_id:
            cur_source_val = item.text
            cur_xml_source.getroot().remove(item)
            cur_xml_source.write(file_dir, encoding="utf-8", xml_declaration=True)
            return cur_source_val

def update_destination_file(destination_module_path, dir_name):
    file_dir = os.path.join(destination_module_path, dir_name, "strings.xml")

    if not os.path.exists(file_dir):
        directory, _ = os.path.split(file_dir)
        os.makedirs(directory, exist_ok=True)
        with open(file_dir, 'w') as f:
            pass
        cur_xml = ET.Element("resources")
        cur_xml_tree = ET.ElementTree(cur_xml)
    else :
        cur_xml_tree = ET.parse(file_dir)
        if len(cur_xml_tree.getroot()):
            cur_xml_tree.getroot()[-1].tail = '\n' + '    '

    new_element = ET.SubElement(cur_xml_tree.getroot(), "string", name=destination_str_id)
    new_element.text = source_str
    new_element.tail = '\n'  # 添加尾部换行符

    cur_xml_tree.write(file_dir, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    check_user_input(sys.argv[1], sys.argv[2])
    source_module, source_str_id, destination_module, destination_str_id = get_user_input(sys.argv[1], sys.argv[2])
    print(f"source_module: {source_module}, source_str_id: {source_str_id}")
    print(f"destination_module: {destination_module}, destination_str_id: {destination_str_id}")

    source_module_path = get_dir_path(source_module)
    destination_module_path = get_dir_path(destination_module)

    for dir_name in os.listdir(source_module_path):
        if dir_name.startswith("values"):
            source_str = update_source_file_and_get_str(source_module_path, dir_name)
            update_destination_file(destination_module_path, dir_name)