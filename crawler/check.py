import re
import random
import requests
from collections import Counter

HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}
def get_all_proj_urls(file_url: str):
    std = lambda x: x.replace('\\n', '').replace('\\t1', '').replace('\n', '')
    with open(file_url, "r") as f:
        java_proj_url = map(std, f.readlines())
    
    return list(set(java_proj_url))


def check_created_time(proj_url_storage_file_url: str) -> Counter:
    pass

if __name__ == "__main__":
    x = get_all_proj_urls("/data/hieuvd/lvdthieu/maven_projects/uncompilable.txt")
    x.remove("")
    x1 = random.choices(x, k=60)
    with open("uncompilable_proj.txt", "w") as f:
        for i in x1:
            f.write(i+'\n')




    
