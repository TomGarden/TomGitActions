又到了夏天, 蝉又要叫了

## 0x00. 做了一个什么?

一个个人博客程序 : 通过 github actions 将 github repository 中的 markdown 文件发布到该 repository 的 issues 中 .

抄自 : https://github.com/Sep0lkit/git-issues-blog 

## 0x01. 局限性

### 1.1. markdown 链接语法替换问题
对 markdown 中的链接语法 `[](http 巴拉巴拉)` 支持的不够完善 .

当前是通过 EL(Expression Language) 表达式完成的匹配与替换

```python
# 甚至在我贴出这段代码的时候我都在担心这段代码会把我贴出的这段代码给替换的啥都不是了 , 细想了一下发现没问题 😁
# 局限性的问题的一个表现就是还需要想一下

def replace_markdown_links(input_str: str, path: str) -> str:
    pattern = r'\[(.*?)\]\((?!http)(.*?)\)'
    re_format = "[\\1](https://raw.githubusercontent.com/{}/{}/{}/\\2)".format(
        GITHUB_REPO, GITHUB_BRANCH, path)
    result = re.sub(pattern, re_format, input_str, flags=re.M)
    return result
```

关于这个规则如果看到的你有更好的改进方案 , 我很乐意修正这个实现细节


### 1.2. git 文件变化识别问题
```python

class ModifyEnum(enum.Enum):
    """
    规范: https://git-scm.com/docs/git-diff#Documentation/git-diff.txt-git-diff-filesltpatterngt82308203

    下述修改我们
        知道怎么触发的标记为 [√]
        不知道怎么触发的标记为 [x] //未成功测试处理的修改类型, 通过 git diff 文档给定的格式进行操作

    [√] A: addition of a file
    [x] C: copy of a file into a new one
    [√] D: deletion of a file
    [√] M: modification of the contents or mode of a file
    [√] R: renaming of a file
    [x] T: change in the type of the file
    [x] U: file is unmerged (you must complete the merge before it can be committed)
    [x] X: "unknown" change type (most probably a bug, please report it)
    """
    modify_addition = 'A'
    modify_copy = 'C'
    modify_deletion = 'D'
    modify_modification = 'M'
    modify_renaming = 'R'
    modify_file_is_unmerged = 'U'

    modify_change_type = 'T'
    modify_unknown = 'X'

```

## 0x02. 文件内容

如果想查看实现细节或者自己有兴趣实现一次 , `.github` 文件中留有各种文件和说明

## 0x03. 关于使用方式

### 3.1. 比较简单的方式
1. github create a public repository 
    - 创建一个 issue 作为映射文件的存放地址(注意 issues 内容为空) 
    - 记下 issue 编号
2. create directory and files
    - clone the repository
    - repository-root/.github/github_host.yml  :
        ```yaml
        # 工作流程的名称。 GitHub 在仓库的操作页面上显示工作流程的名称。
        name: github_host-action-issue-blog
        
        
        # 下文含义为 *******************************************
        #     当 master 分支发生 push 事件时针对 paths
        #     中指定的文件时执行 jobs(作业)
        # *****************************************************
        on: # 触发工作流程的 GitHub 事件的名称。
          push:
            branches:
              - master
        
        # 工作流程运行包括一项或多项作业。
        # 作业默认是并行运行。
        # 要按顺序运行作业，您可以使用 <job_id>needs 关键词在其他作业上定义依赖项。
        jobs:
        
          publish_your_repository_files:
      
            runs-on: macos-latest
        
            steps: # 一个 job(作业) 可以分为若干 step(步骤)
      
              - uses: TomGarden/TomGitActions@0.1.0
                  # 这里的环境变量可以在脚本中使用
                  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
                  # 必选配置项
                  ISSUES_MAP_FILE_NUMBER:  '9'
                  ISSUES_CONFIG: '.github/github_actions/issues_config.json'
                  # 可选配置项
                  GITHUB_BRANCH:  'master'
                  ISSUES_FOOTER_PATH:  '.github/github_actions/issues_footer.md'
                  ISSUES_HEADER_PATH:  '.github/github_actions/issues_header.md'
        ```
    
    - (Optional) repository-root/.github/github_actions/issues_footer.md
    - (Optional) repository-root/.github/github_actions/issues_header.md

### 3.2. 比较复杂的方式(可控性高)
我还没有仔细研究
1. clone repository , 将 .github 文件拷贝到自己 repository
2. 在自己的项目手动创建一个 issue , 可以有标题, 内容一定要为空, 就是没有内容
    - 当然也可以是有内容的, 前提是你得知道自己在做什么
    - 把这个 issue 的 id (就是从 1 开始计数的那个数字)放到这里:
        - `.github/workflows/github_host.yml` 文件的 `ISSUES_MAP_FILE_NUMBER:  '9'`
3. 阅读此文件注释 `.github/github_actions/issues_config.json`
4. 至此已经可以是用了
5. 关于其他配置细节
    - `ISSUES_FOOTER_PATH:  '.github/github_actions/issues_footer.md'`
    - `ISSUES_HEADER_PATH:  '.github/github_actions/issues_header.md'`



## 0x04. 实现细节

### 4.1. 主流程
1. 全程 `yml` 居中调度
2. `install_dependence_xxx.sh` 安装依赖 (python . 等)
3. `git_action_practice.py` 实现从 repository 到 issue 的负值粘贴

### 4.2. `git_action_practice.py`细节
1. 通过 `pygithub` 和 `requsts` 调用 `github api`
    实现 repository 文件的拉取 和 issues 内容的上传
2. 通过 `git log` 获取仓库变化时间和 哈希
3. 通过 `git diff` 根据按仓库变化的 哈希 获取变化的文件路径和
4. 维护一个 `repository : issue` 的文件映射持久化到 一个指定的 issue 中(json 格式) . 
    这个文件也记录上次成功执行的 `commit hash`
5. DONE


## 0x06. 其他内容

证明文件链接有一定可用性
- [制作过程草稿 · 诸多未竟 RAW](.github/document/制造过程草稿.md)
    - [markdown 格式 , 你看这又是一个小问题 😁](https://github.com/TomGarden/TomGitActions/blob/master/.github/document制造过程草稿.md)
    - 这里有我想过但没有试试的细节们
    - 这里有我碰到的困难和解决办法们

证明图片链接有一定可用性
- ![截图一张](images/2020-05-28_22:12:17.jpg)