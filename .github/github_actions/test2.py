import json
import logging

ISSUES_DICTIONARY_MAP = {
    '.github/workflows/main.yml': 1,
    '.github/workflows/github_host.yml': 2,
    '你好啊': 3
}

request_data = json.dumps(ISSUES_DICTIONARY_MAP, ensure_ascii=False, indent=2)
print(request_data)

request_data2 = json.dumps(ISSUES_DICTIONARY_MAP)
print(request_data2)
