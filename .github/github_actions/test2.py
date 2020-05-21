import re


def match_issue_ignore_ary(path_str: str, issue_ignore_line) -> bool:
    """

    :param path_str: 一个即将处理的路径
    :param issue_ignore_line: 一条忽略规则
    :return: true, 二者匹配 , 文件应该被忽略
             false,  不匹配 , 文件不应该被忽略
    """

    # 连续多个路径符号被替换为单个路径符号



issues_dictionary_map_key: [
    "a/b/c/d/e/f/g.md"
    "aa/bb/cc/dd/ee/ff/gg.md",
    "aa/aa/cc/dd/ee/ff/gg.md",
]

test = "\S*"
test_str = "*abc"
pattern = re.compile(r'o' + test_str)

if pattern.match("oooabc"):
    print('ok')
else:
    print('failed')
