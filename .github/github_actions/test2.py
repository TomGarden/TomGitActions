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


def test() -> []:
    return None


test_ary = test()
if test_ary is None:
    print(2546347)
if isinstance(test_ary, type(None)):
    print("124")
else:
    print("456")
