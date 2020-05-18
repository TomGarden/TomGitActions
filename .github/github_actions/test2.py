import logging
# import json
# import subprocess
#
# import requests
# from urllib3 import request
#
# # json_str = "{'url': 'https://api.github.com/repos/TomGarden/TomGitActions/issues/2', 'repository_url': 'https://api.github.com/repos/TomGarden/TomGitActions', 'labels_url': 'https://api.github.com/repos/TomGarden/TomGitActions/issues/2/labels{/name}', 'comments_url': 'https://api.github.com/repos/TomGarden/TomGitActions/issues/2/comments', 'events_url': 'https://api.github.com/repos/TomGarden/TomGitActions/issues/2/events', 'html_url': 'https://github.com/TomGarden/TomGitActions/issues/2', 'id': 613864472, 'node_id': 'MDU6SXNzdWU2MTM4NjQ0NzI=', 'number': 2, 'title': 'README', 'user': {'login': 'TomGarden', 'id': 22384291, 'node_id': 'MDQ6VXNlcjIyMzg0Mjkx', 'avatar_url': 'https://avatars2.githubusercontent.com/u/22384291?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/TomGarden', 'html_url': 'https://github.com/TomGarden', 'followers_url': 'https://api.github.com/users/TomGarden/followers', 'following_url': 'https://api.github.com/users/TomGarden/following{/other_user}', 'gists_url': 'https://api.github.com/users/TomGarden/gists{/gist_id}', 'starred_url': 'https://api.github.com/users/TomGarden/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/TomGarden/subscriptions', 'organizations_url': 'https://api.github.com/users/TomGarden/orgs', 'repos_url': 'https://api.github.com/users/TomGarden/repos', 'events_url': 'https://api.github.com/users/TomGarden/events{/privacy}', 'received_events_url': 'https://api.github.com/users/TomGarden/received_events', 'type': 'User', 'site_admin': False}, 'labels': [], 'state': 'open', 'locked': False, 'assignee': None, 'assignees': [], 'milestone': None, 'comments': 0, 'created_at': '2020-05-07T08:16:32Z', 'updated_at': '2020-05-15T13:11:10Z', 'closed_at': None, 'author_association': 'OWNER', 'body': '', 'closed_by': None}"
# # json_obj = json.loads(json_str)
# #
# # print(json_obj)
# GITHUB_TOKEN = "c6e2348638441d50564c548d8e2581ce0c1fea83"
# header = {'Authorization': 'token %s' % GITHUB_TOKEN}
# reponse = requests.get("https://api.github.com/repos/TomGarden/TomGitActions/issues/1", headers=header)
# print(reponse)
# print(reponse.content)
import json
import os
import subprocess


# args = ['git', 'diff', '--raw', '-z', '--line-prefix=///', '1ab8aedf4f079aa01c5d1c256660a01a9b08316b']
# completed_process = subprocess.run(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#
# stdout: str = completed_process.stdout
# stderr: str = completed_process.stderr

def logger(*args, sep=' ', end='\n', file=None):
    print(*args, sep, end)


args = ["git", "diff", "--raw", "-z", "--line-prefix=line_prefix"]
# print(args)

logger(args)
print(args)



logging.root.setLevel(logging.NOTSET)

logging.debug("debug \t细节信息，仅当诊断问题时适用。")

logging.info("info \t确认程序按预期运行")

logging.warning("warning \t表明有已经或即将发生的意外（例如：磁盘空间不足）。程序仍按预期进行")

logging.error("error \t由于严重的问题，程序的某些功能已经不能正常执行")

logging.critical("critical \t严重的错误，表明程序已不能继续执行")

def test():
    try:
        raise Exception("堆栈信息")
    except Exception as e:
        logging.exception(e)

test()

logging.info("bala")
