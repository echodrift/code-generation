import re
import random
import requests
from collections import Counter, namedtuple
import pandas as pd
from tqdm import tqdm


HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}
Proj_info = namedtuple("Proj_info", "full_name created_at star")


def get_all_proj_urls(file_url: str):
    std = lambda x: x.replace('\\n', '').replace('\\t1', '').replace('\n', '')
    with open(file_url, "r") as f:
        java_proj_url = map(std, f.readlines())
    
    return list(set(java_proj_url))


def check_created_time(proj_url_storage_file_url: str) -> pd.DataFrame:
    with open(proj_url_storage_file_url, "r") as f:
        proj_urls = f.read().split('\n')
    
    proj_infos = []
    for proj_url in tqdm(proj_urls):
        try:
            response = requests.get(proj_url, headers=HEADERS).json()
            proj_infos.append(Proj_info(full_name=response["full_name"], 
                                    created_at=response["created_at"], 
                                    star=response["stargazers_count"]))
        except:
            with open("error.txt", "a") as f:
                f.write(proj_url + '\n')
    return pd.DataFrame(proj_infos)


if __name__ == "__main__":
    pass




    
