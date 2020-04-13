## 进度
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

## 参数释义
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

## 快链
- [自托管](https://help.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)
- [Docker](https://docs.docker.com/engine/reference/builder/)


## 自托管错误列表
- paths 节点写的路径名错误导致 GitHub 站点不展示我们的工作流，这个错误没有任何异常，一句一句测出来的。
- 当设置了 paths 当提交没有执行应该是 paths 中的文件没有变化，如果path 中的文件发生变化才会再次执行
- 替换 uses 字段为 `TomGarden/TomGitActions@master` 之后自托管阻塞， GitHub-host 失败
    - 尝试修改项目为公开再试仍然报错
        `
- Could not find file '/home/runner/work/_actions/_temp_17ef85be-8371-4695-be54-0df83e36a30f/_staging/TomGarden-TomGitActions-c276e39/venv/bin/python3`
    - 这时在使用 idea 创建的 Python 项目的文件夹，把这个文件忽略掉就没问题了
    
- 自托管工作流不执行可以到本地日志文件查找问题
    - [Reviewing a job's log file](https://help.github.com/cn/actions/hosting-your-own-runners/monitoring-and-troubleshooting-self-hosted-runners#reviewing-a-jobs-log-file)

