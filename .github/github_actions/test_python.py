import enum
import os
import re
import json
import pathlib
import requests
import subprocess
import urllib.parse
from github import Github
from github import GithubException
from github import UnknownObjectException

from ignore_dir.debug_utils import debug_init_os_env

# region 文件伪代码
# 伪代码.md 文件中也有部分逻辑
## 预备
# 1. 所有受支持的文件编码均为 utf-8
#
## 主流程伪代码
# 1. 获取仓库中的配置文件 issues_dictionary_map
# 2. 获取上个更新时间点之后的仓库变化 文件 cur_opt_files_list
# 3. if (cur_opt_files_list 存在于 issues_dictionary_map）:
#         更新对应文件对应的 issues 可能的操作有 : 增删改查
#         同时更新 issues_dictionary_map
# 4. 再次持久化 issues_dictionary_map
#
## 其他操作
# 1. 全程日志记录
# 2. 操作结束持久化日志
# 3. 邮件通知
#
## 子流程 · 主流程的补充
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
## 配置项
#

# 设置脚本的当前工作目录
os.chdir("/Volumes/document/script_language/TomGitActions")
debug_init_os_env()

GITHUB_API = "https://api.github.com"
GITHUB_ACTION_NAME = os.environ['GITHUB_ACTION']

# Get environment variables 环境变量中的值都是可以配置的需要出具配置相关文档
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
GITHUB_USER = os.environ['GITHUB_REPOSITORY_OWNER']
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'master')
POSTS_PATH = os.getenv('POSTS_PATH', '../posts')
ISSUES_DICTIONARY_MAP_FILE = os.getenv('ISSUES_DICTIONARY_MAP_FILE', '_issues_dictionary_map.json')
ISSUES_NUMBER = os.getenv('ISSUES_NUMBER', 9)

# 命令行输出文件的间隔符
git_log_line_separator = "···@/@···"
git_log_line_separator_newline = git_log_line_separator + "\n"
git_diff_line_prefix = "///"
git_diff_line_separator = "\x00"
git_diff_line_separator_newline = git_diff_line_separator + "\n"

# 持久化的 json 文件中的 key 字符串
LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY = "last_success_opt_commit_log_line_key"
ISSUES_DICTIONARY_MAP_KEY = "issues_dictionary_map_key"

# issues 和 repository 文件的映射
JSON_OBJ = {}
ISSUES_DICTIONARY_MAP = {}
LAST_SUCCESS_OPT_COMMIT_LOG_LINE = ""


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


# github object
# github_obj = Github(login_or_token=GITHUB_TOKEN)
github_obj = Github(login_or_token=GITHUB_TOKEN, base_url=GITHUB_API)
repo = github_obj.get_repo(GITHUB_REPO)


def get_issues_file_dictionary_form_issue(_issue_number: int = ISSUES_NUMBER):
    _issue = repo.get_issue(_issue_number)

    json_str = _issue.body

    global JSON_OBJ
    global LAST_SUCCESS_OPT_COMMIT_LOG_LINE
    global ISSUES_DICTIONARY_MAP

    if len(json_str) > 0 and \
            json_str.startswith('```json') and \
            json_str.endswith('```'):
        print("get_issues_file_dictionary_form_issue(_issue_number)   SUCCESS(with json content)   ···"
              .format(_issue_number))

        json_str = json_str[7:len(json_str) - 3]

        JSON_OBJ = json.loads(json_str)
        LAST_SUCCESS_OPT_COMMIT_LOG_LINE = JSON_OBJ[LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY]
        ISSUES_DICTIONARY_MAP = JSON_OBJ[ISSUES_DICTIONARY_MAP_KEY]

    elif not isinstance(json_str, str) or \
            len(json_str) == 0:
        print("get_issues_file_dictionary_form_issue(_issue_number)   SUCCESS(content is empty)   ···"
              .format(_issue_number))

    else:
        raise Exception("get_issues_file_dictionary_form_issue(_issue_number)   FAILED(unknown err)")


def get_issues_file_dictionary_form_file(file_name: str):
    issues_dictionary_map_file_obj = pathlib.Path(file_name)
    if issues_dictionary_map_file_obj.exists():
        with open(file_name, encoding='utf-8', mode='r') as file:
            global JSON_OBJ
            global LAST_SUCCESS_OPT_COMMIT_LOG_LINE
            global ISSUES_DICTIONARY_MAP
            JSON_OBJ = json.load(file)
            LAST_SUCCESS_OPT_COMMIT_LOG_LINE = JSON_OBJ[LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY]
            ISSUES_DICTIONARY_MAP = JSON_OBJ[ISSUES_DICTIONARY_MAP_KEY]


def persistence_file_dictionary_map_to_issue(_issue_number: int = ISSUES_NUMBER):
    """将 json 信息持久化到指定 issue"""
    JSON_OBJ[LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY] = commit_log_range[0]
    JSON_OBJ[ISSUES_DICTIONARY_MAP_KEY] = ISSUES_DICTIONARY_MAP
    json_str = json.dumps(JSON_OBJ)

    issue_update(_issue_number, "映射文件", "```json{json_str}```".format(json_str=json_str))


def logger(string: str):
    print(string)


def get_hash_form_commit_log_line(last_success_opt_commit_log_line: str) -> str or None:
    """
    :param last_success_opt_commit_log_line: git log 格式化输出的一行中获取 commit hash
    :return: 参数中包含的 commit hash , 为 None 表示没有有效的 commit , 表示尚未提交过任何内容
    """

    if last_success_opt_commit_log_line is None or \
            not isinstance(last_success_opt_commit_log_line, str) or \
            len(last_success_opt_commit_log_line) == 0:
        return None

    return last_success_opt_commit_log_line.split(git_log_line_separator, 1)[0]


def get_time_form_commit_log_line(last_success_opt_commit_log_line: str) -> str or None:
    """
    :param last_success_opt_commit_log_line: git log 格式化输出的一行中获取 commit 的提交时间
    :return: 参数中包含的 commit 的提交时间
    """

    # 校验入参合法性
    if last_success_opt_commit_log_line is None or \
            not isinstance(last_success_opt_commit_log_line, str) or \
            len(last_success_opt_commit_log_line) == 0:
        return None

    str_array: [] = last_success_opt_commit_log_line.split(git_log_line_separator, 2)
    if len(str_array) < 2:
        raise Exception("入参格式异常, 获取 commit 时间失败")

    return str_array[1]


def get_current_opt_commit_log_line_range(_last_commit_time: str) -> []:
    """
    获取我们即将处理的 commit 区间, 一首一位两行格式化 commit 日志行
    核心命令: git log --pretty=format:"%H - %cd : %s" --date=format:'%Y-%m-%d %H:%M:%S %z'

    :param _last_commit_time: 上次处理的次 commit 的时间
                             None 表示尚未处理过任何 commit
    :return: 返回我们关心的 commit 区间,
                result[0] 表示时间上最晚的提交
                result[1] 表示时间上最早的提交
    """

    args = ["git", "log", "--date=format:%Y-%m-%d %H:%M:%S %z",
            "--pretty=format:'%H{separator}%cd{separator}%s{separator}'".format(separator=git_log_line_separator)]

    if _last_commit_time is not None:
        args.append("--since='{commit_time}'".format(commit_time=_last_commit_time))

    completed_process = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout: str = completed_process.stdout
    stderr: str = completed_process.stderr

    if stderr is not None and \
            len(stderr) > 0:
        logger("{method_name}({param}) --> err msg : \n\t{errmsg}".
               format(method_name='get_current_opt_commit_log_line_range', param=_last_commit_time, errmsg=stderr))

    if stdout is None:
        return None

    line_array: [] = stdout.split(git_log_line_separator_newline)
    if len(line_array) <= 2:
        return line_array
    else:
        return [line_array[0], len(line_array) - 1]


def get_diff_from_commits(_after_commit_hash: str, _earlier_commit_hash: str) -> []:
    """

    核心命令: git diff --raw -z 9a24fc6aae05744253912999e2b5ba3a7f44600f dcc69f4762b60257a281dd408d8ed701241ed13d

    :param _after_commit_hash: 时间上靠后的的 commit hash 值
                             None 表示尚未处理过任何 commit
    :param _earlier_commit_hash:  时间上靠前的 commit hash 值
                             None 首次提交, 无需提供
    :return: 非空,最新的文件变化列表 ;
             如果为空意味着, repository 没有发生变化
    """

    args = ["git", "diff", "--raw", "-z", "--line-prefix={line_prefix}".format(line_prefix=git_diff_line_prefix)]

    if _earlier_commit_hash is not None:
        args.append(_earlier_commit_hash)

    if _after_commit_hash is None or \
            not isinstance(_after_commit_hash, str) or \
            len(_after_commit_hash) == 0:
        raise Exception("last_commit_hash 值 异常 ,这是异常值")
    else:
        args.append(_after_commit_hash)

    completed_process: subprocess.CompletedProcess = \
        subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout: str = completed_process.stdout
    stderr: str = completed_process.stderr

    if stderr is not None and \
            len(stderr) > 0:
        logger("{method_name}({after_param},{earlier_param}) --> err msg : \n\t{errmsg}".
               format(method_name='get_diff_from_commits', after_param=_after_commit_hash,
                      earlier_param=_earlier_commit_hash, errmsg=stderr))

    _git_diff_line_list: [] = stdout.split(git_diff_line_prefix)

    if len(_git_diff_line_list) > 0 and len(_git_diff_line_list[0]) == 0:
        _git_diff_line_list = _git_diff_line_list[1:]

    return _git_diff_line_list


def issue_update(_issue_number: int, _issue_title: str = None, _issue_body: str = None) -> bool:
    """
    更新指定 issue >>> `https://developer.github.com/v3/issue/#update-an-issue`

    :param _issue_number: 当前 issue 对应的 issue id
    :param _issue_title: issue 标题
    :param _issue_body: issue 内容
    :return: true 更新内容成功 , false 更新出错
    """

    # 获取 issue 内容
    _issue = repo.get_issue(_issue_number)
    print(_issue)

    # 获取 issue url
    _issue_url = _issue.url

    # 解析并更新 issue 内容
    # issue_obj = _issue.raw_data
    # issue_obj['title'] = _issue_title
    # issue_obj['body'] = _issue_body
    issue_obj = {
        'title': _issue_title,
        'body': _issue_body
    }

    # 设置更新请求 header
    patch_header = {'Authorization': 'token %s' % GITHUB_TOKEN}

    # 先设置代理在发起请

    # 发起更新 issue 请求
    request_data = json.dumps(issue_obj).encode('utf-8').decode('unicode_escape')
    response = requests.patch(_issue_url, headers=patch_header, data=request_data)

    update_result = response.status_code == 200

    if not update_result:
        print(response)
        print(response.content)
        logger("更新 issue 失败, _issue_number = {}".format(_issue_number))

    return update_result


def issue_get(_issue_number):
    requests.get()


def issue_opt(new_file: str, old_file: str = None):
    """
    给定两个文件路径, 用于更新 issue 内容

    :param old_file: 不一定有值, 如果有意味着要更新文件
    :param new_file: 一定有值, 本次操作的核心文件
    :return:
    """

    if new_file is None or len(new_file) == 0:
        raise Exception("异常参数: {}".format(new_file))

    file_desc = pathlib.Path(new_file)

    if not file_desc.exists():
        logger("issue_opt({new_file}) : 文件不存在".format(new_file=new_file))
        return

    _issue_title = file_desc.name
    with open(file_desc, encoding='utf-8', mode='r') as file_stream:
        _issue_body = file_stream.read()
        file_stream.close()

    if old_file is None or \
            len(old_file) == 0:
        if new_file in ISSUES_DICTIONARY_MAP:
            update_result = issue_update(ISSUES_DICTIONARY_MAP[new_file], _issue_title, _issue_body)
        else:
            _issue = repo.create_issue(_issue_title, _issue_body)
            ISSUES_DICTIONARY_MAP[new_file] = _issue.number
        pass
    else:
        if old_file in ISSUES_DICTIONARY_MAP:
            update_result = issue_update(ISSUES_DICTIONARY_MAP[old_file], _issue_title, _issue_body)
        else:
            _issue = repo.create_issue(_issue_title, _issue_body)
            ISSUES_DICTIONARY_MAP[new_file] = _issue.number


def opt_dif_line(git_diff_line: str):
    """
    操作 git diff 的返回行

    :param git_diff_line:
    :return:
    """

    if git_diff_line is None or \
            not isinstance(git_diff_line, str) or \
            len(git_diff_line) < 31:
        logger("{method_name}({param}) --> err msg : \n\t{errmsg}".
               format(method_name='opt_dif_line', param=git_diff_line, errmsg="无法识别的参数格式"))
        return
    else:
        temp_git_diff_line: str = git_diff_line[31:]

    def verify_one_path_log_ary(one_path_ary: []) -> bool:
        return len(one_path_ary) == 3 and len(one_path_ary[2]) == 0

    def verify_two_path_log_ary(two_path_ary: []) -> bool:
        return len(two_path_ary) == 4 and len(two_path_ary[3]) == 0

    first_char = temp_git_diff_line[0]
    path_ary: [] = temp_git_diff_line.split(git_diff_line_separator)

    if first_char == ModifyEnum.modify_addition.value:
        if verify_one_path_log_ary(path_ary):
            issue_opt(path_ary[1])
        else:
            logger("增加文件失败 : " + git_diff_line)
            pass
        pass
    elif first_char == ModifyEnum.modify_deletion.value:
        if verify_one_path_log_ary(path_ary):
            if ISSUES_DICTIONARY_MAP.pop[path_ary[1], True]:
                logger("删除文件失败-2 : " + git_diff_line)
        else:
            logger("删除文件失败-1 : " + git_diff_line)
            pass

        pass
    elif first_char == ModifyEnum.modify_modification.value:
        path_ary: [] = temp_git_diff_line.split(git_diff_line_separator)
        if verify_one_path_log_ary(path_ary):
            issue_opt(path_ary[1])
            pass
        else:
            logger("更新文件内容失败 : " + git_diff_line)
            pass
        pass
    elif first_char == ModifyEnum.modify_file_is_unmerged.value:
        path_ary: [] = temp_git_diff_line.split(git_diff_line_separator)
        if verify_one_path_log_ary(path_ary):
            issue_opt(path_ary[1])
            pass
        else:
            logger("操作 unmerged 文件失败 : " + git_diff_line)
            pass
        pass
    elif first_char == ModifyEnum.modify_copy.value:
        path_ary: [] = temp_git_diff_line.split(git_diff_line_separator)
        if verify_two_path_log_ary(path_ary):
            issue_opt(path_ary[2])
            pass
        else:
            logger("操作拷贝文件失败 : " + git_diff_line)
            pass
        pass
    elif first_char == ModifyEnum.modify_renaming.value:
        path_ary: [] = temp_git_diff_line.split(git_diff_line_separator)
        if verify_two_path_log_ary(path_ary):
            issue_opt(path_ary[2])
            pass
        else:
            logger("重命名文件文件失败 : " + git_diff_line)
            pass
        pass
    elif first_char == ModifyEnum.modify_change_type.value:
        logger("未知操作 \t " + git_diff_line)
        pass
    elif first_char == ModifyEnum.modify_unknown.value:
        logger("未知错误操作 \t " + git_diff_line)
        pass


# 加载持久化的 json 文件获取上一次操作的信息
get_issues_file_dictionary_form_issue()

# 获取上次操作到的那个 commit 的提交时间
last_commit_time: str = get_time_form_commit_log_line(LAST_SUCCESS_OPT_COMMIT_LOG_LINE)

# 获取我们关心的 commit 范围(从给定时间开始, 到最后一次)
commit_log_range: [] = get_current_opt_commit_log_line_range(last_commit_time)

# 我们关心的时间上较晚的 commit hash (也就是最后一次提交的 commit hash)
after_commit_hash: str = get_hash_form_commit_log_line(commit_log_range[0])

# 我们关心的时间上较早的 commit hash (也就是上一次 action 操作的 commit hash)
if len(commit_log_range) > 1:
    earlier_commit_hash: str = get_hash_form_commit_log_line(commit_log_range[1])
else:
    earlier_commit_hash = None

# 从两个 commit hash 通过 git diff 命令获取在两个 commit 之间发生变化的文件列表
git_diff_line_list: [] = get_diff_from_commits(after_commit_hash, earlier_commit_hash)

# 遍历变化的文件日志行,逐行处理变化的文件,(或更新现有文件,或创建新文件)
for a_git_diff_line in git_diff_line_list:
    opt_dif_line(a_git_diff_line)

# 操作完成重新持久化 json 文件
persistence_file_dictionary_map_to_issue()

exit('手动终止,没有含义')

#######################################################################################
#############                         重构逻辑分割线                     #################
#######################################################################################


# 最后一次执行 acton 操作的时间戳
LAST_ACTION_TIME_STAMP = "__last_opt_time_stamp__"

# Global variables
POSTS = []
CHANGED = []

# region local dictionary 获取可上传的文件路径集合
issues_dictionary_map_file = pathlib.Path(ISSUES_DICTIONARY_MAP_FILE)
if issues_dictionary_map_file.exists():
    try:
        with open(ISSUES_DICTIONARY_MAP_FILE, encoding='utf-8', mode='r') as file:
            ISSUES_DICTIONARY_MAP = json.load(file)

        last_action_time_stamp = ISSUES_DICTIONARY_MAP[LAST_ACTION_TIME_STAMP]
        lastcommit = ISSUES_DICTIONARY_MAP['__commit__']
        command = "git diff --name-only -z " + lastcommit
        changed = subprocess.check_output(['git', 'diff', '--name-only', '-z', lastcommit])
        for x in changed.split(b'\x00'):
            if x.decode('utf-8'):
                CHANGED.append(x.decode('utf-8'))
        file.close()
    except Exception as e:
        print('%s load error: %s' % (ISSUES_DICTIONARY_MAP_FILE, e))
        exit(-1)

post_path = pathlib.Path(POSTS_PATH)
for file in post_path.rglob('*.md'):
    # 根据目录获取指定文件的思路不适合我们的需求，我们应该根据提交信息或者时间两个属性来确定那个文件应该更新
    if len(CHANGED) != 0:
        if (file.as_posix() in CHANGED):
            print("post %s need update" % file.as_posix())
            POSTS.append(file)
    else:
        POSTS.append(file)

print("posts need update: ")
print(POSTS)

header = pathlib.Path('_tpl/post-header.md')
if header.exists():
    issue_header = header.read_text()
else:
    issue_header = ""

footer = pathlib.Path('_tpl/post-footer.md')
if footer.exists():
    issue_footer = footer.read_text()
else:
    issue_footer = "\n\nPowered by [Git-Issues-Blog](https://github.com/marketplace/actions/git-issues-blog)"


# endregion local dictionary 获取可上传的文件路径集合

# issues tpl variables function 模板变量设定
def parse_issue_tpl(content, user, path):
    # GITHUB_POSTS_USER
    content = re.sub(r'{{\s?GITHUB_POSTS_USER\s?}}', user, content, flags=re.M)
    # GITHUB_POSTS_FILENAME
    postname = path.rsplit('/', 1)[1]
    content = re.sub(r'{{\s?GITHUB_POSTS_NAME\s?}}', postname, content, flags=re.M)
    # GITHUB_POSTS_URL
    url = "https://github.com/{}/blob/{}/{}".format(GITHUB_REPO, GITHUB_BRANCH, urllib.parse.quote(path))
    content = re.sub(r'{{\s?GITHUB_POSTS_URL\s?}}', url, content, flags=re.M)

    return content


for one_post_file in POSTS:
    # issue content templat)e   读取文件内容
    with open(one_post_file, encoding='utf-8', mode='r') as file_stream:
        issue_body = file_stream.read()
        file_stream.close()

        # relative link to raw.github link , 把文件中相匹配的路径替换成 github 路径
        re_format = "![\\1](https://raw.githubusercontent.com/{}/{}/{}/\\2)".format(
            GITHUB_REPO, GITHUB_BRANCH, one_post_file.parent.as_posix())
        issue_body_with_giturl = re.sub(r'!\[(.*)\]\((?!http)(.*)\)', re_format, issue_body, flags=re.M)

    # template variables in header and footer 替换 header 和 footer 中的锚点字符串
    issue_header_with_tpl = parse_issue_tpl(issue_header, GITHUB_USER, one_post_file.as_posix())
    issue_footer_with_tpl = parse_issue_tpl(issue_footer, GITHUB_USER, one_post_file.as_posix())

    issue_content = issue_header_with_tpl + issue_body_with_giturl + issue_footer_with_tpl

    # check file exist issue or not by title(POSTS_PATH)  校验 issus 是否已经存在
    pstr = one_post_file.as_posix()
    if pstr in ISSUES_DICTIONARY_MAP:
        # get issue info
        issue_number = ISSUES_DICTIONARY_MAP[pstr]
        try:
            issue = repo.get_issue(number=issue_number)

            issue_url = issue.html_url
            issue_title = issue.title

            # content
            payload = {
                'title': issue_title,
                'body': issue_content
            }

            # github edit issue api
            header = {'Authorization': 'token %s' % GITHUB_TOKEN}

            url = GITHUB_API + "/repos/" + GITHUB_REPO + "/issues/" + str(issue_number)
            r = requests.patch(url, headers=header, data=json.dumps(payload))
            if r.status_code == 200:
                print("issue update successful: %s" % issue_number)
            else:
                print("issue update failed: %s" % issue_number)
                exit(-1)
        except GithubException as e:
            print('get issues: %s error, skip for next' % issue_number)

    else:
        # creat issue
        title = one_post_file.name
        title = re.sub('.md$', '', title, flags=re.IGNORECASE)
        issue = repo.create_issue(title, issue_content)
        print("issue create successfule: %s" % issue.number)
        ISSUES_DICTIONARY_MAP[pstr] = issue.number

commit = os.environ['GITHUB_SHA']
print("update posts to commit id: %s" % commit)
if re.search("^\w{40}$", commit):
    ISSUES_DICTIONARY_MAP['__commit__'] = commit
else:
    print('last commit id got error')
    exit(-1)

# write posts index and commit step
try:
    repo.get_contents(ISSUES_DICTIONARY_MAP_FILE, ref=GITHUB_BRANCH)
except UnknownObjectException:
    repo.create_file(ISSUES_DICTIONARY_MAP_FILE, "add post index: _index", "{}", branch=GITHUB_BRANCH)
# update POST_INDEX_FILE
post_index_file = repo.get_contents(ISSUES_DICTIONARY_MAP_FILE, ref=GITHUB_BRANCH)
post_index_content = json.dumps(ISSUES_DICTIONARY_MAP, ensure_ascii=False)
post_index_msg = "rebuild posts index from: " + GITHUB_ACTION_NAME
repo.update_file(post_index_file.path, post_index_msg, post_index_content, post_index_file.sha, branch=GITHUB_BRANCH)

print("posts update successful")
