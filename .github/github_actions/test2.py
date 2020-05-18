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


issue_obj = {
    'title': "我是标题",
    'body': "我是内容, English"
}
issue_obj_str: str = json.dumps(issue_obj).encode('utf-8').decode('unicode_escape')
if isinstance(issue_obj_str, str):
    print("dumps之后是 str")
else:
    print("dumps之后非 str")
print(os.getcwd())
print(issue_obj_str)

issue_obj_str = "```json{content}```".format(content=issue_obj_str)
print(issue_obj_str)

if issue_obj_str.startswith('```json') and \
        issue_obj_str.endswith('```'):
    print("巴拉巴拉")
else:
    print("小魔仙")
