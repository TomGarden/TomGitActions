import logging
import re

issue_body2 = "balabasdfasdf[adf](asdf) gkj ![我是本地图片链接](images/截屏2020-05-23.png)![我是远程图片链接](https://raw.githubusercontent.com/TomGarden/Tetris/master/images/First.png)"
issue_body = "[1](1)  [2](2)"

pattern = r'\[(.*)\]\((?!http)(.*)\)'


def replace_markdown_links(input_str: str) -> str:
    re_format = "[\\1](https://raw.githubusercontent.com/{}/{}/{}/\\2)".format(
        "GITHUB_REPO", "GITHUB_BRANCH", "one_post_file.parent.as_posix")
    issue_body_with_giturl = re.sub(pattern, re_format, issue_body, flags=re.M)

    print(issue_body_with_giturl)
    pass


replace_markdown_links(issue_body)

result = re.findall(pattern, issue_body)
print(result)
