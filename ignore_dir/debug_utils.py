import os


# 设置必要的环境变量 调用本函数前的环境变量内容 [`print(os.environ)`]
# {
# 	"PATH": "/Volumes/beyourself/dev_tools/dev_kit/python_pro_venv/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
# 	"PYTHONPATH": "/Volumes/document/script_language/TomGitActions",
# 	"SHELL": "/bin/zsh",
# 	"PAGER": "less",
# 	"LSCOLORS": "Gxfxcxdxbxegedabagacad",
# 	"PYTHONIOENCODING": "UTF-8",
# 	"OLDPWD": "/Applications/PyCharm CE.app/Contents/bin",
# 	"USER": "tom",
# 	"ZSH": "/Users/tom/.oh-my-zsh",
# 	"TMPDIR": "/var/folders/9v/hnbg2nb96jxd4g6chtwv8dlw0000gn/T/",
# 	"PS1": "(python_pro_venv) ",
# 	"SSH_AUTH_SOCK": "/private/tmp/com.apple.launchd.bozW88tZPl/Listeners",
# 	"VIRTUAL_ENV": "/Volumes/beyourself/dev_tools/dev_kit/python_pro_venv",
# 	"XPC_FLAGS": "0x0",
# 	"PYTHONUNBUFFERED": "1",
# 	"VERSIONER_PYTHON_VERSION": "2.7",
# 	"__CF_USER_TEXT_ENCODING": "0x1F5: 0x19: 0x34",
# 	"LESS": "-R",
# 	"LOGNAME": "tom",
# 	"LC_CTYPE": "zh_CN.UTF-8",
# 	"XPC_SERVICE_NAME": "com.jetbrains.pycharm.3724",
# 	"PWD": "/Volumes/document/script_language/TomGitActions/ignore_dir",
# 	"PYCHARM_HOSTED": "1",
# 	"HOME": "/Users/tom",
# 	"__PYVENV_LAUNCHER__": "/Volumes/beyourself/dev_tools/dev_kit/python_pro_venv/bin/python"
# }
def debug_init_os_env():
    os.environ["GITHUB_ACTION"] = "run"
    os.environ["GITHUB_TOKEN"] = "737f51b1a9ce658e2522f1f3e284bde50f1fe101"
    os.environ['GITHUB_REPOSITORY'] = "TomGarden/TomGitActions"
    os.environ['GITHUB_REPOSITORY_OWNER'] = "TomGarden"
    os.environ['POSTS_PATH'] = "posts"

# 删除临时设置的环境变量
def debug_del_os_env():
    del os.environ["GITHUB_ACTION"]
    del os.environ["GITHUB_TOKEN"]
    del os.environ['GITHUB_REPOSITORY']
    del os.environ['GITHUB_REPOSITORY_OWNER']
    del os.environ['POSTS_PATH']


# print(os.environ)
# debug_init_os_env()
# print(os.environ)
# debug_del_os_env()
# print(os.environ)
