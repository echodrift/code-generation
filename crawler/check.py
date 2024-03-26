import re
# def check_duplicates(file_url: str):
#     std = lambda x: x.replace('\\n', '').replace('\\t1', '').replace('\n', '')
#     with open(file_url, "r") as f:
#         java_proj_url = map(std, f.readlines())
    
#     return set(java_proj_url)

# x1 = check_duplicates("/data/hieuvd/lvdthieu/maven_projects/uncompilable.txt")
# x2 = check_duplicates("/data/hieuvd/lvdthieu/maven_projects/compilable.txt")

# x1.remove('')
# x2.remove('')
# print("/data/hieuvd/lvdthieu/maven_projects/compilable.txt" in x1)
# print(len(x2))
# with open("compilable_proj.txt", "w") as f:
#     for proj in x2:
#         try:
#             tmp = proj.split('/')[-1].split('_')
#             if len(tmp) == 2:
#                 f.write(f"https://api.github.com/repos/{tmp[0]}/{tmp[1]}"'\n')
#         except:
#             pass
# print(len(x1 | x2))
import requests
from collections import Counter

HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}

def check_created_time(proj_url_storage_file_url: str) -> Counter:
    """Use github api to search repo
    """
    with open(proj_url_storage_file_url, "r") as f:
        proj_urls = f.read().split('\n')
    
    for proj_url in proj_urls:
        # print(repr(proj_url))
        response = requests.get(proj_url, HEADERS)
        print(response.json())
        break
if __name__ == "__main__":
    check_created_time("all_url_v1.txt")



    
