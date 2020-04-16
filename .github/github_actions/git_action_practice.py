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
g = Github(GITHUB_TOKEN)
github_obj = Github()
repo = g.get_repo(GITHUB_REPO)

print("卖报的小行家")
print(os.environ)