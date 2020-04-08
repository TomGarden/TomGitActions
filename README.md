1. 尝试直接在本地创建 yaml 文件并设置 py 文件与之关联。
    - 但是上传代码后 actions 列表中没有任何内容
2. 通过 GitHub 引导创建一个 yaml 文件后 actions 中成功出现合法 action
    - pull 到本地， 删除 GitHub 创建的 yaml 再次 push ， 观察到 actions 列表中的 actions 并没有消失
    - 恢复刚删除的 yaml 文件
    - 拷贝一个副本， 修改 yaml 中关于 action 命名代码， 执行 push
        - 重新点击 Actions 标签， 即可看到新的 action
3. 所以接下来我们需要了解语法细节了，因为自托管的 action ，没有出现在 Actions 列表中，也没有执行


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


## 自托管错误列表
- paths 节点写的路径名错误导致 GitHub 站点不展示我们的工作流，这个错误没有任何异常，一句一句测出来的。
- 当设置了 paths 当提交没有执行应该是 paths 中的文件没有变化，如果path 中的文件发生变化才会再次执行

