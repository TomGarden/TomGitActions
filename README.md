## 0x00. 进度
1. 尝试直接在本地创建 yaml 文件并设置 py 文件与之关联。
    - 但是上传代码后 actions 列表中没有任何内容
2. 通过 GitHub 引导创建一个 yaml 文件后 actions 中成功出现合法 action
    - pull 到本地， 删除 GitHub 创建的 yaml 再次 push ， 观察到 actions 列表中的 actions 并没有消失
    - 恢复刚删除的 yaml 文件
    - 拷贝一个副本， 修改 yaml 中关于 action 命名代码， 执行 push
        - 重新点击 Actions 标签， 即可看到新的 action
3. 所以接下来我们需要了解语法细节了，因为自托管的 action ，没有出现在 Actions 列表中，也没有执行
4. 现在 github-host 可以运行，self-host 的无法运行这个问题需要解决，否则调试不方便
    - 现象是 self-host 的都在队列中但是不执行
    - 尝试到本地日志文件查找端倪
        - 日志文件名字为 ： `Runner_20200409-080001-utc` 
        - 定位字段之后的日志即为异常：`[2020-04-09 12:38:55Z WARN GitHubActionsService] Retrieving an AAD auth token took a long time (2.1094582 seconds)`
        - 这个异常是在执行 [再次测试 self-host](https://github.com/TomGarden/TomGitActions/actions/runs/74114980) 的时候出现的
    - 别忘了更新[自己的提问帖](https://github.community/t5/GitHub-Actions/self-host-block-on-Starting-your-workflow-run/m-p/53309/highlight/false#M8781)
    - 尝试手动下载文件，文件下载位置应该是错误了，这么做无效
    - 尝试手动下载并下载旧版本重新安装新版本后再试一次

## 0x01. 参数释义
- jobs.<job_id>.steps.uses
- {owner}/{repo}@{ref}

```
steps:    
  - uses: actions/setup-node@74bc508 # Reference a specific commit
  - uses: actions/setup-node@v1      # Reference the major version of a release   
  - uses: actions/setup-node@v1.2    # Reference a minor version of a release  
  - uses: actions/setup-node@master  # Reference a branch
*****************************************************************************
steps:    
  - uses: TomGarden/TomGitActions@74bc508 # Reference a specific commit
  - uses: TomGarden/TomGitActions@v1      # Reference the major version of a release   
  - uses: TomGarden/TomGitActions@v1.2    # Reference a minor version of a release  
  - uses: TomGarden/TomGitActions@master  # Reference a branch
```

## 0x02. 快链
- [任务记录追踪](https://trello.com/b/5PH6gxbZ/队列)
- [自托管](https://help.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)
- [Docker](https://docs.docker.com/engine/reference/builder/)
- [self-host 使用 docker 只支持 Linux 平台](https://help.github.com/cn/actions/building-actions/creating-a-docker-container-action)
- [shell 教程](https://www.gnu.org/software/bash/manual/)
    - 《linux shell脚本攻略》
- [Mac 换源](https://lug.ustc.edu.cn/wiki/mirrors/help/brew.git)
    - [Mac 换源 2](https://www.zhihu.com/question/31360766)
- [Python](https://docs.python.org/zh-cn/3/)
    - [python 代码风格指南](https://www.python.org/dev/peps/pep-0008/)
        - [某个中文版本](https://pythonguidecn.readthedocs.io/zh/latest/writing/style.html#pep-8)
    - [PyGithub 开发文档](https://pygithub.readthedocs.io/en/latest/)
    - [对类中的 self 的理解](https://docs.python.org/zh-cn/3/tutorial/classes.html)
- [关于 GitHub 的访问权限](https://developer.github.com/apps/about-apps/)

### 2.1. 限制须知
1. 在编码调试阶段我们不再在本地真正运行 host-actions 而是直接使用 PyGitHub 远程操作 GitHub 仓库
    - https://developer.github.com/v3/#rate-limiting
        - 对于使用基本身份验证或OAuth的API请求，您每小时最多可以进行5000个请求。
        - 对于未经身份验证的请求，速率限制允许每小时最多60个请求。 
    - [查看当前请求限制数据](https://pygithub.readthedocs.io/en/latest/github.html#github.MainClass.Github.rate_limiting)
        ```python
        rateLimiting = github_obj.rate_limiting
        print(rateLimiting)
        ```



## 0x03. 自托管错误列表
- paths 节点写的路径名错误导致 GitHub 站点不展示我们的工作流，这个错误没有任何异常，一句一句测出来的。
- 当设置了 paths 当提交没有执行应该是 paths 中的文件没有变化，如果path 中的文件发生变化才会再次执行
- 替换 uses 字段为 `TomGarden/TomGitActions@master` 之后自托管阻塞， GitHub-host 失败
    - 尝试修改项目为公开再试仍然报错
        `
- Could not find file '/home/runner/work/_actions/_temp_17ef85be-8371-4695-be54-0df83e36a30f/_staging/TomGarden-TomGitActions-c276e39/venv/bin/python3`
    - 这时在使用 idea 创建的 Python 项目的文件夹，把这个文件忽略掉就没问题了
    
- 自托管工作流不执行可以到本地日志文件查找问题
    - [Reviewing a job's log file](https://help.github.com/cn/actions/hosting-your-own-runners/monitoring-and-troubleshooting-self-hosted-runners#reviewing-a-jobs-log-file)

