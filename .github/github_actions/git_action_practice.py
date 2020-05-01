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

GITHUB_API = "https://api.github.com"
GITHUB_ACTION_NAME = os.environ['GITHUB_ACTION']

# Get environment variables
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
GITHUB_USER = os.environ['GITHUB_REPOSITORY_OWNER']
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'master')
POSTS_PATH = os.getenv('POSTS_PATH', 'posts')
POST_INDEX_FILE = os.getenv('POST_INDEX_FILE', '_index')

# Global variables
POSTS = []
CHANGED = []

# github object
github_obj = Github(GITHUB_TOKEN)
repo = github_obj.get_repo(GITHUB_REPO)

# local dictionary
dictionary = {}
index = pathlib.Path(POST_INDEX_FILE)
print(index)
if index.exists():
    print("TomLog >>> index exists")
    try:
        with open(POST_INDEX_FILE, encoding='utf-8', mode='r') as f:
            dictionary = json.load(f)
        # lastcommit = dictionary['__commit__']
        # command = "git diff --name-only -z " + lastcommit
        # changed = subprocess.check_output(['git', 'diff', '--name-only', '-z', lastcommit])
        # for x in changed.split(b'\x00'):
        #     if x.decode('utf-8'):
        #         CHANGED.append(x.decode('utf-8'))
        f.close()
    except Exception as e:
        print('%s load error: %s' % (POST_INDEX_FILE, e))
        exit(-1)

else:
    print("TomLog >>> index not exists")

print(dictionary)
