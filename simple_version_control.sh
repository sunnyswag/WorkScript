#!/bin/bash

###
# 功能说明：
# 1. 从 versions.gradle 获取当前版本名称。
# 2. 使用版本名称为当前提交打上标签。
# 3. 将版本标签推送到远程git仓库。
# 4. 更新版本号，将其值增加一。
# 5. 更新版本名称，将其最后部分的值增加一。
# 6. 提交这些更改并将它们推送到远程git仓库。
#
# 使用说明：
# chmod +x simple_version_control.sh
# ./simple_version_control.sh
###


# 获取 ./versions.gradle 文件中的 app_versions.version_name 字段值
version_name=$(grep -o 'app_versions.version_name = "[^"]*' ./versions.gradle | sed 's/app_versions.version_name = "//')
echo "Current version: $version_name"

# 使用当前版本号为 Git 打上 tag 并推送到远程仓库
git tag "v$version_name"
git push origin "v$version_name"


# update version code
version_code=$(grep -o 'app_versions.version_code = [0-9]*' ./versions.gradle | sed 's/app_versions.version_code = //')

# 将 version_code 增加 1
new_version_code=$((version_code + 1))

if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/app_versions.version_code = $version_code/app_versions.version_code = $new_version_code/g" ./versions.gradle
else
    sed -i "s/app_versions.version_code = $version_code/app_versions.version_code = $new_version_code/g" ./versions.gradle
fi

# 提交版本号更新并推送到远程仓库
git add ./versions.gradle
git commit -m "Update version code to $new_version_code"


# update version name
IFS='.' read -ra version_parts <<< "$version_name"
new_version="${version_parts[0]}.${version_parts[1]}.$((version_parts[2])).$((version_parts[3] + 1))"

if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/app_versions.version_name = \"$version_name\"/app_versions.version_name = \"$new_version\"/g" ./versions.gradle
else
    sed -i "s/app_versions.version_name = \"$version_name\"/app_versions.version_name = \"$new_version\"/g" ./versions.gradle
fi
git add ./versions.gradle
git commit -m "Update version to $new_version"

# 输出更新后的版本号
echo "new version: $new_version, new version code: $new_version_code"
git push