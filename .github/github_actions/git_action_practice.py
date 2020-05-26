import enum
import json
import logging
import os
import pathlib
import re
import subprocess

import requests
from github import Github

logging.root.setLevel(logging.INFO)


# 设置脚本的当前工作目录
os.chdir(os.path.abspath(os.path.join(os.getcwd(), "../..")))

GITHUB_API = "https://api.github.com"
GITHUB_ACTION_NAME = os.environ['GITHUB_ACTION']

# Get environment variables 环境变量中的值都是可以配置的需要出具配置相关文档
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
GITHUB_USER = os.environ['GITHUB_REPOSITORY_OWNER']
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'master')
POSTS_PATH = os.getenv('POSTS_PATH', '../posts')
ISSUES_DICTIONARY_MAP_FILE = os.getenv('ISSUES_DICTIONARY_MAP_FILE', '_issues_dictionary_map.json')
ISSUES_CONFIG = os.getenv('ISSUES_CONFIG', '.github/github_actions/issues_config.json')
ISSUES_FOOTER_PATH = os.getenv('ISSUES_FOOTER_PATH', '.github/github_actions/issues_footer.md')
ISSUES_HEADER_PATH = os.getenv('ISSUES_HEADER_PATH', '.github/github_actions/issues_header.md')
ISSUES_NUMBER = os.getenv('ISSUES_NUMBER', 9)

# 命令行输出文件的间隔符
git_log_line_separator = "···@/@···"
git_log_line_separator_newline = git_log_line_separator + "\n"
git_diff_line_prefix = "///"
git_diff_line_separator = "\x00"
git_diff_line_separator_newline = git_diff_line_separator + "\n"

# issues 和 repository 文件的映射
JSON_OBJ = {}
ISSUES_DICTIONARY_MAP_KEY = "issues_dictionary_map_key"
ISSUES_DICTIONARY_MAP = {}
LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY = "last_success_opt_commit_log_line_key"
LAST_SUCCESS_OPT_COMMIT_LOG_LINE = ""

# issue 忽略文件的数组
ISSUES_IGNORE_ARRAY_KEY = "issues_ignore"
ISSUES_IGNORE_ARRAY = []

# 支持的文件类型数组
ISSUES_SUPPORT_FILE_TYPE_ARRAY_KEY = "issues_support_file_type"
ISSUES_SUPPORT_FILE_TYPE_ARRAY = []


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


def get_issues_file_dictionary_form_issue(_issue_number: int = ISSUES_NUMBER):
    _issue = repo.get_issue(_issue_number)

    json_str = _issue.body

    global JSON_OBJ
    global LAST_SUCCESS_OPT_COMMIT_LOG_LINE
    global ISSUES_DICTIONARY_MAP

    if len(json_str) > 0 and \
            json_str.startswith('```json') and \
            json_str.endswith('```'):
        logging.info("get_issues_file_dictionary_form_issue(_issue_number)   SUCCESS(with json content)   ···"
                     .format(_issue_number))

        json_str = json_str[7:len(json_str) - 3]

        JSON_OBJ = json.loads(json_str)
        LAST_SUCCESS_OPT_COMMIT_LOG_LINE = JSON_OBJ[LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY]
        ISSUES_DICTIONARY_MAP = JSON_OBJ[ISSUES_DICTIONARY_MAP_KEY]

    elif not isinstance(json_str, str) or \
            len(json_str) == 0:
        logging.info("get_issues_file_dictionary_form_issue(_issue_number)   SUCCESS(content is empty)   ···"
                     .format(_issue_number))

    else:
        raise Exception("get_issues_file_dictionary_form_issue(_issue_number)   FAILED(unknown err)")


def get_issues_file_dictionary_form_file(file_name: str):
    issues_dictionary_map_file_obj = pathlib.Path(file_name)
    if issues_dictionary_map_file_obj.exists():
        with open(issues_dictionary_map_file_obj, encoding='utf-8', mode='r') as file:
            global JSON_OBJ
            global LAST_SUCCESS_OPT_COMMIT_LOG_LINE
            global ISSUES_DICTIONARY_MAP
            JSON_OBJ = json.load(file)
            LAST_SUCCESS_OPT_COMMIT_LOG_LINE = JSON_OBJ[LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY]
            ISSUES_DICTIONARY_MAP = JSON_OBJ[ISSUES_DICTIONARY_MAP_KEY]


def get_issues_config_from_file(file_name: str):
    issues_configfile_obj = pathlib.Path(file_name)
    if issues_configfile_obj.exists():
        with open(issues_configfile_obj, encoding='utf-8', mode='r') as file:
            global ISSUES_IGNORE_ARRAY
            global ISSUES_SUPPORT_FILE_TYPE_ARRAY
            json_obj = json.load(file)
            ISSUES_IGNORE_ARRAY = json_obj[ISSUES_IGNORE_ARRAY_KEY]
            ISSUES_SUPPORT_FILE_TYPE_ARRAY = json_obj[ISSUES_SUPPORT_FILE_TYPE_ARRAY_KEY]


def persistence_file_dictionary_map_to_issue(_issue_number: int = ISSUES_NUMBER):
    """将 json 信息持久化到指定 issue"""
    JSON_OBJ[LAST_SUCCESS_OPT_COMMIT_LOG_LINE_KEY] = commit_log_range[0]
    JSON_OBJ[ISSUES_DICTIONARY_MAP_KEY] = ISSUES_DICTIONARY_MAP
    json_str = json.dumps(JSON_OBJ, ensure_ascii=False, indent=2)

    issue_update(_issue_number, "映射文件", "```json\n{json_str}\n```".format(json_str=json_str))


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
             返回值可能为空数组, 如果数组为空表示没有更新提交内容, 应该停止脚本运行
    """

    args = ["git", "log", "--date=format:%Y-%m-%d %H:%M:%S %z",
            "--pretty=format:%H{separator}%cd{separator}%s{separator}".format(separator=git_log_line_separator)]

    if _last_commit_time is not None:
        args.append("--since='{commit_time}'".format(commit_time=_last_commit_time))

    completed_process = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout: str = completed_process.stdout
    stderr: str = completed_process.stderr

    if stderr is not None and \
            len(stderr) > 0:
        logging.warning("{method_name}({param}) --> err msg : \n\t{errmsg}".
                        format(method_name='get_current_opt_commit_log_line_range', param=_last_commit_time,
                               errmsg=stderr))

    if stdout is None:
        return None

    line_array: [] = stdout.split(git_log_line_separator_newline)

    if len(line_array) > 0:
        index: int = len(line_array) - 1
        item = line_array[index]
        line_array[index] = item[0:len(item) - len(git_log_line_separator)]

    if len(line_array) == 1 and line_array[0] == LAST_SUCCESS_OPT_COMMIT_LOG_LINE:
        return []
    if len(line_array) <= 2:
        return line_array
    else:
        return [line_array[0], line_array[len(line_array) - 1]]


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

    logging.info(args)

    completed_process: subprocess.CompletedProcess = \
        subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout: str = completed_process.stdout
    stderr: str = completed_process.stderr

    logging.info(stdout)

    if stderr is not None and \
            len(stderr) > 0:
        logging.warning("{method_name}({after_param},{earlier_param}) --> err msg : \n\t{errmsg}".
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
    request_data = json.dumps(issue_obj, ensure_ascii=False, indent=2).encode()
    response = requests.patch(_issue_url, headers=patch_header, data=request_data)

    update_result = response.status_code == 200

    if not update_result:
        logging.error(response)
        logging.error(response.content)
        logging.error("更新 issue 失败, _issue_number = {}".format(_issue_number))

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

    if match_issue_ignore_ary(new_file, ISSUES_IGNORE_ARRAY):
        logging.info("\t文件:{file}被忽略".format(file=new_file))
        return

    if new_file is None or len(new_file) == 0:
        raise Exception("异常参数: {}".format(new_file))

    file_desc = pathlib.Path(new_file)

    if not file_desc.exists():
        logging.error("issue_opt({new_file}) : 文件不存在".format(new_file=new_file))
        return

    _issue_title = file_desc.name

    with open(file_desc, encoding='utf-8', mode='r') as file_stream:
        _issue_body = file_stream.read()
        _issue_body = replace_markdown_links(_issue_body, file_desc.parent.as_posix())
        _issue_header = read_file_text(ISSUES_HEADER_PATH)
        _issue_footer = read_file_text(ISSUES_FOOTER_PATH)
        _issue_body = _issue_header + _issue_body + _issue_footer
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


def replace_markdown_links(input_str: str, path: str) -> str:
    pattern = r'[^`]\[(.*?)\]\((?!http)(.*?)\)'
    re_format = "[\\1](https://raw.githubusercontent.com/{}/{}/{}/\\2)".format(
        GITHUB_REPO, GITHUB_BRANCH, path)
    result = re.sub(pattern, re_format, input_str, flags=re.M)
    return result


def read_file_text(path: str) -> str:
    file = pathlib.Path(path)
    if file.exists():
        return file.read_text()
    else:
        return ""


def opt_dif_line(git_diff_line: str):
    """
    操作 git diff 的返回行

    :param git_diff_line:
    :return:
    """

    logging.info("正在操作😁[没有消息就是好消息]:" + git_diff_line)

    if git_diff_line is None or \
            not isinstance(git_diff_line, str) or \
            len(git_diff_line) < 31:
        logging.warning("{method_name}({param}) --> err msg : \n\t{errmsg}".
                        format(method_name='opt_dif_line', param=git_diff_line, errmsg="无法识别的参数格式"))
        return
    else:
        temp_git_diff_line: str = git_diff_line[31:]

    def verify_one_path_log_ary(one_path_ary: []) -> bool:
        return len(one_path_ary) == 3 and len(one_path_ary[2]) == 0

    def verify_two_path_log_ary(two_path_ary: []) -> bool:
        return len(two_path_ary) == 4 and len(two_path_ary[3]) == 0

    def opt_first_path(modify: str):
        if verify_one_path_log_ary(path_ary):
            try:
                if match_issue_support_file_type(path_ary[1], ISSUES_SUPPORT_FILE_TYPE_ARRAY):
                    issue_opt(path_ary[1])
                else:
                    logging.info("文件类型原因忽略文件: " + path_ary[1])
            except Exception as exception:
                logging.error(modify + "失败,请查看堆栈信息")
                logging.exception(exception)
                return
        else:
            logging.error(modify + "失败(意外的格式) : \n\t" + git_diff_line)
            pass
        pass

    first_char = temp_git_diff_line[0]
    path_ary: [] = temp_git_diff_line.split(git_diff_line_separator)

    if first_char == ModifyEnum.modify_addition.value:
        opt_first_path("添加文件")
    elif first_char == ModifyEnum.modify_deletion.value:
        if verify_one_path_log_ary(path_ary):
            if ISSUES_DICTIONARY_MAP.pop(path_ary[1], True):
                logging.error("删除文件成功 : " + git_diff_line)
            else:
                logging.error("删除文件失败-2 : " + git_diff_line)
        else:
            logging.error("删除文件失败-1 : " + git_diff_line)
            pass

        pass
    elif first_char == ModifyEnum.modify_modification.value:
        opt_first_path("修改文件")
    elif first_char == ModifyEnum.modify_file_is_unmerged.value:
        opt_first_path("unmerged 文件")
    elif first_char == ModifyEnum.modify_copy.value:
        if verify_two_path_log_ary(path_ary):
            try:
                if match_issue_support_file_type(path_ary[2], ISSUES_SUPPORT_FILE_TYPE_ARRAY):
                    issue_opt(path_ary[2])
                else:
                    logging.info("文件类型原因忽略拷贝文件: " + path_ary[2])
            except Exception as exception:
                logging.error("操作拷贝文件失败,请查看堆栈信息")
                logging.exception(exception)
            pass
        else:
            logging.error("操作拷贝文件失败 : " + git_diff_line)
            pass
        pass
    elif first_char == ModifyEnum.modify_renaming.value:
        if verify_two_path_log_ary(path_ary):
            try:
                if match_issue_support_file_type(path_ary[2], ISSUES_SUPPORT_FILE_TYPE_ARRAY):
                    issue_opt(path_ary[1], path_ary[2])
                else:
                    logging.info("文件类型原因忽略重命名文件: " + path_ary[2])
            except Exception as exception:
                logging.error("重命名文件文件失败,请查看堆栈信息")
                logging.exception(exception)
            pass
        else:
            logging.error("重命名文件文件失败 : " + git_diff_line)
            pass
        pass
    elif first_char == ModifyEnum.modify_change_type.value:
        logging.error("未知操作 \t " + git_diff_line)
        pass
    elif first_char == ModifyEnum.modify_unknown.value:
        logging.error("未知错误操作 \t " + git_diff_line)
        pass
    else:
        logging.error("未知操作 \t " + git_diff_line)


def match_issue_ignore_ary(path_str: str, issue_ignore_ary: []) -> bool:
    """
    当前值做简单的文件路径字符串匹配

    :param issue_ignore_ary: 忽略路径
    :param path_str:  文件路径
    :return: true, 二者匹配 , 文件应该被忽略
             false,  不匹配 , 文件不应该被忽略
    """

    if path_str is None or \
            len(path_str) == 0:
        # 无效内容应该被忽略
        return True

    if issue_ignore_ary is None or \
            len(issue_ignore_ary) == 0:
        return False

    for issue_ignore in issue_ignore_ary:
        if path_str.startswith(issue_ignore):
            # 只要有一个匹配就忽略该文件
            return True

    return False


def match_issue_support_file_type(file_path: str, support_file_type: []) -> bool:
    """
    file_path 是否以 support_file_type 中某个元素为结尾
    :param file_path:  先转为小写字符在做比较
    :param support_file_type:
    :return: true 文件是被支持的类型应该处理, false 文件类型不被支持
    """
    return file_path.lower().endswith(tuple(support_file_type))


logging.info("\t登陆 github  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
github_obj = Github(login_or_token=GITHUB_TOKEN, base_url=GITHUB_API)
repo = github_obj.get_repo(GITHUB_REPO)

logging.info("\t加载持久化的 json 文件获取上一次操作的信息>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
get_issues_file_dictionary_form_issue()

logging.info("\t加载忽略规则>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
get_issues_config_from_file(ISSUES_CONFIG)

logging.info("\t获取上次操作到的那个 commit 的提交时间>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
last_commit_time: str = get_time_form_commit_log_line(LAST_SUCCESS_OPT_COMMIT_LOG_LINE)
logging.info("\t 从 `{last_commit_log_line}` 获取到的上次操作的时间为:\t`{last_commit_time}`"
             .format(last_commit_log_line=LAST_SUCCESS_OPT_COMMIT_LOG_LINE, last_commit_time=last_commit_time))

logging.info("\t获取我们关心的 commit 范围(从给定时间开始, 到最后一次)>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
commit_log_range: [] = get_current_opt_commit_log_line_range(last_commit_time)
logging.info(commit_log_range)
if commit_log_range is None or len(commit_log_range) == 0:
    exit("未检测到更新内容, action 停止运行")

logging.info("\t我们关心的时间上较晚的 commit hash (也就是最后一次提交的 commit hash)>>>>>>>>>>>>>>>>>>>")
after_commit_hash: str = get_hash_form_commit_log_line(commit_log_range[0])
logging.info("\t{}".format(after_commit_hash))

logging.info("\t我们关心的时间上较早的 commit hash (也就是上一次 action 操作的 commit hash)>>>>>>>>>>>>>")
if len(commit_log_range) > 1:
    earlier_commit_hash: str = get_hash_form_commit_log_line(commit_log_range[1])
else:
    earlier_commit_hash = None
logging.info("\t{}".format(earlier_commit_hash))

logging.info("\t从两个 commit hash 通过 git diff 命令获取在两个 commit 之间发生变化的文件列表>>>>>>>>>>>>")
git_diff_line_list: [] = get_diff_from_commits(after_commit_hash, earlier_commit_hash)
logging.info("要处理的发生变化的文件列表:")
logging.info(git_diff_line_list)

logging.info("\t遍历变化的文件日志行,逐行处理变化的文件,(或更新现有文件,或创建新文件)>>>>>>>>>>>>>>>>>>>>>>>>")
for a_git_diff_line in git_diff_line_list:
    opt_dif_line(a_git_diff_line)

logging.info("\t操作完成重新持久化 json 文件>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
persistence_file_dictionary_map_to_issue()

print('脚本执行完毕 , 手动终止')
