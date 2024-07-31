#!/bin/bash

checkout_new_branch () {
  time=$(date "+%Y%m%d_%H%M%S")
  save_msg=$(git stash save $time | head -n 1)

  git checkout master
  git pull origin master
  git checkout -b personal/huiqinhuang_$time remotes/origin/master

  if [[ ! ("$save_msg" == "No local changes to save") ]]; then
    git stash pop
  fi

  echo "Pop stash: $save_msg"
}

last_branch=$(git symbolic-ref --short HEAD)
checkout_new_branch

if [[ "$last_branch" == *personal/huiqinhuang* ]]; then
  git branch -D "$last_branch"
fi