import os
import requests
from typing import List
import json
from tqdm import tqdm
from collections import Counter

HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}


def search_repo(store_search_result_url: str):
    page = 1
    all_elements = []
    while page <= 20:
        print("Current page:", page)
        url = f"https://api.github.com/search/repositories?q=language:java&sort=star&order=desc&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            break
        cur_page_elements = response.json()
        all_elements += cur_page_elements["items"]
        page += 1
        
    with open(store_search_result_url, "w") as f:
        json.dump(all_elements, f)


def get_all_project_url(store_search_result_url: str):
    with open(store_search_result_url, "r") as f:
        repos = json.loads(f.read())
    
    repo_urls = [repo["html_url"] for repo in repos]
    return repo_urls


def check_clone(store_cloned_project_url: str):
    pass

if __name__ == "__main__":
    project_urls = get_all_project_url("repos.json")
    project_names = []
    tmp = 0
    for project_url in project_urls:
        tmp = project_url.split('/')
        project_names.append((tmp[-2], tmp[-1]))

    project_user, project_repo = zip(*project_names)
    counter = Counter(project_repo)
    unique_projects = {}
    for repo in counter:
        if counter[repo] == 1:
            unique_projects[repo] = True
        else:
            unique_projects[repo] = False
    with open("not_unique_repos.txt", "w") as f:
        for project_name in project_names:
            if not unique_projects[project_name[1]]:
                f.write(f"https://github.com/{project_name[0]}/{project_name[1]}" + ';' + project_name[0] + ';' + project_name[1] + '\n')

