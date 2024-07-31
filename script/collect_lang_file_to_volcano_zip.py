import os
import tempfile
import shutil
import re

MODULE_NAME_MACHTER = r'(.+?)[/\\]src[/\\]main[/\\]res'
STRING_FILE_NAME = "strings.xml"
CURRENT_DIR = ".{}".format(os.sep)
DEFAULT_FILE_NAME = "default"
LANG_NAME_MAPPER = {
    "values": "source",
    "values-en": "en-US",
    "values-zh-rTW": "zh-TW",
    "values-ko-rKR": "ko-KR"
}

def check_file_exists(full_res_path):
    result = []
    error_dir_names = []

    for name, _ in LANG_NAME_MAPPER.items():
        strings_xml_path = os.path.join(full_res_path, name, STRING_FILE_NAME)
        path_exists = os.path.exists(strings_xml_path)
        result.append(path_exists)

        if not path_exists:
            error_dir_names.append(name)

    if all(result):
        return True
    else:
        if not (len(error_dir_names) == len(LANG_NAME_MAPPER) \
                or (len(error_dir_names) == len(LANG_NAME_MAPPER) - 1 and "values" not in error_dir_names)):
            print("\033[38;5;178m please check dir path: {}\033[0m".format(full_res_path))
            print("\033[38;5;178m check subdir is correct name or not : {}\033[0m".format(error_dir_names))
        return False

def get_all_res_dir(source_dir):
    res_directories = []
    for dirpath, dirnames, _ in os.walk(source_dir):
        if "build" not in dirpath and "res" in dirnames:
            full_res_path = os.path.join(dirpath, "res")
            if check_file_exists(full_res_path):
                res_directories.append(full_res_path)

    return res_directories

def archive_string_file(res_dir, output_dir):
    with tempfile.TemporaryDirectory() as temp_dir:
        for original_dir_name, target_dir_name in LANG_NAME_MAPPER.items():
            original_string_path = os.path.join(res_dir, original_dir_name, STRING_FILE_NAME)

            target_dir_path = os.path.join(temp_dir, target_dir_name)
            os.makedirs(target_dir_path)
            shutil.copy(original_string_path, target_dir_path)

        shutil.make_archive(output_dir, 'zip', temp_dir)

def get_output_dir(output_path, source_dir, res_dir):
    output_prefix_dir = source_dir.split(os.sep)[-1]
    output_filename = get_output_file_name(source_dir, res_dir)
    print(f"output_path: {output_path} output_prefix_dir: {output_prefix_dir} output_filename: {output_filename}.zip")
    output_dir = os.path.join(output_path, output_prefix_dir, output_filename)
    print("output dir: {}.zip".format(output_dir))
    return output_dir

def get_output_file_name(source_dir, res_dir):
    res_dir = res_dir if source_dir == CURRENT_DIR else res_dir[len(source_dir): ]
    match_res = re.search(MODULE_NAME_MACHTER, res_dir)
    output_filename = match_res.group(1).strip(f".{os.sep}").strip(os.sep) if match_res else DEFAULT_FILE_NAME
    return output_filename

def warn_file_override(output_dir):
    output_file_path = output_dir + ".zip"
    if os.path.exists(output_file_path):
        print(f"\033[38;5;178mfile {output_file_path} will be override !!!\033[0m")


def get_source_dirs():
    input_dirs = input(
        f"运行该脚本, 会自动提取 Android 项目中需要翻译的 strings.xml 文件, 并打包成火山引擎所支持的格式供直接导入.\n"
        "支持输入多个项目目录, 用空格分隔, 回车则在当前目录中寻找并打包: ")
    if len(input_dirs.split()) != 0:
        source_dirs = [x.strip() for x in input_dirs.split()]
    else:
        source_dirs = [CURRENT_DIR]
    print("source_dirs: {}".format(source_dirs))
    return source_dirs


if __name__ == "__main__":
    source_dirs = get_source_dirs()

    output_path = input(f"请输入翻译文件导出的文件夹, 直接回车则导出到当前文件夹: ").strip()
    if not len(output_path):
        output_path = CURRENT_DIR

    for source_dir in source_dirs:
        res_dirs = get_all_res_dir(source_dir)
        if not res_dirs:
            print("dir need to extract not found, please check the Android project path!")
            exit()

        for res_dir in res_dirs:
            print("source files: {}".format(res_dir))

            output_dir = get_output_dir(output_path, source_dir, res_dir)
            warn_file_override(output_dir)
            archive_string_file(res_dir, output_dir)