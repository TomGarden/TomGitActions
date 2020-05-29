- Dockerfile 挺好的, 但是 macos 上不支持, 所以这个文件我没用过

- install_dependence_macos.sh 已经投入使用
- install_dependence_ubuntu.sh 还没调试好, 还无法使用

- issue_config.json 是配置文件, 韩注释不用过多解释
- issue_header.json 是 markdown 文件生成 issue 的时候用做页眉的
- issue_footer.json 是 markdown 文件生成 issue 的时候用做页脚的

- test_xxx.py 是我在开发过程中用于测试的文件, 其中关于 debug_utils.py 的文件内容如下
```python
def debug_init_os_env():
    os.environ["GITHUB_ACTION"] = "run"
    os.environ["GITHUB_TOKEN"] = "省略掉了, 你搞自己的吧"
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
```

github_action 执行过程
1. `./github/workflows/xxx.yml` 文件执行
2. `yml` 中有系列对 shell 和 python 脚本的调用
3. 脚本们执行完毕, 即可查看效果