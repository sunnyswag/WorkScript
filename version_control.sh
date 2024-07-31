#!/bin/bash

###
# 功能说明：
# 1. 检查当前git分支是否为修复 bug 分支。
# 2. 从 versions.gradle 获取当前版本名称。
# 3. 使用当前版本名称为 Git 打上标签，并推送到远程仓库。
# 4. 如果在主分支模式，更新 versions.gradle 文件中的版本号，将其值增加一。
# 5. 如果在主分支模式，新建一个名为release/fixbug_$version_name的分支，并推送到远程仓库，同时更新其中的版本名称。
# 6. 根据当前模式（修复 Bug 或主分支模式），更新 versions.gradle 文件中的版本名称。
# 7. 提交版本名称的更改并将其推送到远程 Git 仓库。
# 9. 是否为 FixBug 分支的判断逻辑：匹配分支名中 fixbug 字段。
# 8. 对于从 release/fixbug_xxx 切海外修 bug 分支的情况。暂时手动切海外的 oversea_release/fixbug_xxx 分支，使用该脚本更新版本号并打 tag
#
# 使用说明：
# chmod +x version_control.sh
# ./version_control.sh
###

update_version_code () {
    version_code=$(grep -o 'app_versions.version_code = [0-9]*' ./versions.gradle | sed 's/app_versions.version_code = //')

    # 将 version_code 增加 1
    new_version_code=$((version_code + 1))

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/app_versions.version_code = $version_code/app_versions.version_code = $new_version_code/g" ./versions.gradle
    else
        sed -i "s/app_versions.version_code = $version_code/app_versions.version_code = $new_version_code/g" ./versions.gradle
    fi
}

current_branch=$(git symbolic-ref --short HEAD)
if [[ ! ("$current_branch" == *fixbug* || "$current_branch" == *master* || "$current_branch" == *main* ) ]]; then
  echo "$current_branch not fixbug, master or main branch, do return!"
  exit
fi

fixBugMode=false

if [[ "$current_branch" == *fixbug* ]]; then
  fixBugMode=true
fi

if [[ "$fixBugMode" == true ]]; then
  echo "You are in a fixbug branch, use fixbug mode."
else
  echo "You are not in a fixbug branch, use main branch mode."
fi

# 获取 ./versions.gradle 文件中的 app_versions.version_name 字段值
version_name=$(grep -o 'app_versions.version_name = "[^"]*' ./versions.gradle | sed 's/app_versions.version_name = "//')
echo "Current version: $version_name"

# 使用当前版本号为 Git 打上 tag 并推送到远程仓库
git tag "v$version_name"
git push origin "v$version_name"

# 更新 ./versions.gradle 文件中的 app_versions.version_code 字段值
# 读取 app_versions.version_code 字段的值
if [[ "$fixBugMode" == false ]]; then
  change_version_info_branch="tool/change_master_version_$version_name"
  echo "change_version_info_branch is set to: $change_version_info_branch"

  git checkout -b "$change_version_info_branch"

  update_version_code

  # 提交版本号更新并推送到远程仓库
  git add ./versions.gradle
  git commit -m "Update version code to $new_version_code"
  git push --set-upstream origin "$change_version_info_branch"
  git push origin "$change_version_info_branch"

  # 如果分支已存在，则切换到分支 release/fixbug_$version_name 并推送到远程仓库
  new_branch="release/fixbug_$version_name"
  if [ `git branch --list $new_branch` ]
  then
      echo "$new_branch already exists."
      git checkout "$new_branch"
      update_version_code
  else
      git checkout -b "$new_branch"
  fi
  # 修改 fixbug 分支中， ./versions.gradle 文件中的 app_versions.version_name 字段值
  IFS='.' read -ra version_parts <<< "$version_name"
  new_version="${version_parts[0]}.${version_parts[1]}.$((version_parts[2])).$((version_parts[3] + 1))"

  if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s/app_versions.version_name = \"$version_name\"/app_versions.version_name = \"$new_version\"/g" ./versions.gradle
  else
      sed -i "s/app_versions.version_name = \"$version_name\"/app_versions.version_name = \"$new_version\"/g" ./versions.gradle
  fi
  git add ./versions.gradle
  git commit -m "Update version to $new_version"

  git push --set-upstream origin "$new_branch"
  git push origin "$new_branch"
  git checkout "$change_version_info_branch"
fi

# 更新 ./versions.gradle 文件中的 app_versions.version_name 字段值
IFS='.' read -ra version_parts <<< "$version_name"
if [[ "$fixBugMode" == true ]]; then
  new_version="${version_parts[0]}.${version_parts[1]}.$((version_parts[2])).$((version_parts[3] + 1))"
else
  new_version="${version_parts[0]}.${version_parts[1]}.$((version_parts[2] + 1)).0"
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/app_versions.version_name = \"$version_name\"/app_versions.version_name = \"$new_version\"/g" ./versions.gradle
else
  sed -i "s/app_versions.version_name = \"$version_name\"/app_versions.version_name = \"$new_version\"/g" ./versions.gradle
fi

# 输出更新后的版本号
echo "Updated version: $new_version"

git add ./versions.gradle
git commit -m "Update version to $new_version"
git push