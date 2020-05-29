又到了夏天, 蝉又要叫了

## 0x00. 做了一个什么?

一个个人博客程序 : 通过 github actions 将 github repository 中的 markdown 文件发布到该 repository 的 issues 中 .

抄自 : https://github.com/Sep0lkit/git-issues-blog 

## 0x01. 局限性

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


## 0x02. 文件内容

如果想查看实现细节或者自己有兴趣实现一次 , `.github` 文件中留有各种文件和说明

## 0x03. 关于使用方式

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
- [制作过程草稿 · 诸多未竟](.github/document/制造过程草稿.md)
    - 这里有我想过但没有试试的细节们
    - 这里有我碰到的困难和解决办法们

证明图片链接有一定可用性
- ![随意截图](images/2020-05-28_22:12:17.jpg)