import json
import logging
import os
import re

string = "前前 ![2020-05-28_22:12:17.jpg](/images/2020-05-28_22:12:17.jpg) 厚厚"


def replace_markdown_links(input_str: str, path: str) -> str:
    pattern = r'\[(.*?)\]\((?!http)(.*?)\)'
    re_format = "[\\1](https://raw.githubusercontent.com/{}/{}/{}/\\2)".format(
        "GITHUB_REPO", "GITHUB_BRANCH", path)
    result = re.sub(pattern, re_format, input_str, flags=re.M)
    return result


print(string)
print(replace_markdown_links(string, "path"))

test_str = "{}"
json_obj = json.loads(test_str)
if "123" in json_obj:
    print( "true")
else:
    print("234")
ISSUES_IGNORE_ARRAY: [] = json_obj["123"]
ISSUES_SUPPORT_FILE_TYPE_ARRAY: [] = json_obj["456"]
