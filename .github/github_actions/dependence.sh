#!/bin/bash -xv

# 校验首个参数所代表的 app 是否已经安装了，如果没有尚未安装就安装它
# 当前不足之处在于无法返回安装结果，默认为安装成功
function install_one_app() {
  if [ -x `command -v $1` ]; then
    echo "$1 has installed"
  else
    printf "begin install %s ......................................................... \n" "$1"
    brew install "$1"
    printf "install %s DONE ......................................................... \n" "$1"
  fi
}

# 校验所有给定的参数，如果代表的应用没有安装就尝试安装
function install_apps() {
  for app in "$@"; do
    install_one_app "$app"
  done
}

# 安装软件
install_apps  jq  python3
python3 -m ensurepip
pip3 --no-cache-dir install --upgrade pip
pip3 install requests PyGithub pathlib