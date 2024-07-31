import sys
import os
from config import *

###
# 脚本说明：根据场景名称生成对应场景动画的配置文件
# 脚本参数：
# 1. 配置文件的输出路径
###

def generate_xml(filename):
    xml_header = '''<?xml version="1.0" encoding="utf-8"?>
<animation-list
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:oneshot="true">\n'''

    xml_footer = '</animation-list>'

    items = []
    for i in range(pictures_each_anim):  # 生成 _00 和 _01
        drawable_name = f"{filename}_{str(i).zfill(2)}"

        item = f'''    <item
        android:duration="{show_time_each_picture}"
        android:drawable="@drawable/{drawable_name}"/>'''

        items.append(item)

    return xml_header + '\n'.join(items) + '\n' + xml_footer

def save_to_xml(filename, output_directory):
    xml_content = generate_xml(filename)
    output_dir = os.path.join(output_directory, f'{filename}.xml')

    with open(output_dir, 'w', encoding='utf-8') as file:
        file.write(xml_content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供一个目录路径！")
        sys.exit(1)

    output_directory = sys.argv[1]

    for scene_file in scene_file_list:
        save_to_xml(scene_file, output_directory)



scene_file_list = [
    'anim_test_file_1',
    'anim_test_file_2',
    'anim_test_file_3',
    'anim_test_file_4'
]

pictures_each_anim = 50
show_time_each_picture = 40