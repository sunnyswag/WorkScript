import os
import re
import subprocess
from resource_check.config import *
import hashlib
import shutil

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
output_metadata = "output-metadata.json"

def get_module_config_from_settings_gradle():
    with open(os.path.join(CUR_PATH, MODULE_CONFIG_FILE_NAME), 'r', encoding='utf-8') as file:
        module_res = [re.search(r"include '(.*?)'\n", i).group(1) for i in file.readlines() if i.startswith(MODULE_TAG)]
        return list(filter(lambda i: "test" not in i, module_res))

def remove_release_files(release_path: str):
    for filename in os.listdir(release_path):
        os.remove(os.path.join(release_path, filename))

def get_new_apk_name(src_file_path):
    with open(src_file_path, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()[-6:]
    return "launcher_{}.skin".format(md5)

def update_disk_files(output_metadata, module_root_path, output_path, src_file_path, new_apk_name):
    release_path = os.path.join(module_root_path, "release")
    remove_release_files(release_path)
    shutil.copyfile(os.path.join(output_path, output_metadata), os.path.join(release_path, output_metadata))
    shutil.copyfile(src_file_path, os.path.join(release_path, new_apk_name))

if __name__ == "__main__":
    for module_path in get_module_config_from_settings_gradle():
        subprocess.run(["./gradlew", "{}:assembleRelease".format(module_path)])
        module_root_path = CUR_PATH + module_path.replace(":", os.path.sep)
        output_path = os.path.join(module_root_path, "build", "outputs", "apk", "release")
        output_file_name = list(filter(lambda i: i.endswith(".apk"), os.listdir(output_path)))[0]
        if not output_file_name:
            print("output apk not found in {}".format(output_path))
            continue

        src_file_path = os.path.join(output_path, output_file_name)
        new_apk_name = get_new_apk_name(src_file_path)
        update_disk_files(output_metadata, module_root_path, output_path, src_file_path, new_apk_name)
        print("src_file_path: ", src_file_path)