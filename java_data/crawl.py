import json
from collections import Counter
from typing import List

import requests

HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}
REPO_METADATA_STORAGE_URL = "repos.json"

class RepoMetadata:
    pass

class Crawler:
    def __init__():
        pass

    def search_repo():
        """Search for all top star public java projects on Github platform using GithubAPI
        """
        page = 1
        all_elements: List[RepoMetadata] = []
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
        return all_elements
    
    def store_repo_metadata(self, repo_metadata: List[RepoMetadata], storage_url: str):
        """Store repo metadata into a file

        Args:
            repo_metadata (List[RepoMetadata]): Github repositories metadata
            storage_url (str): File url to store
        """
        with open(storage_url, "w") as f:
            json.dump(repo_metadata, f)

    def get_repo_html_url(self, storage_url: str) -> List[str]:
        with open(storage_url, "r") as f:
            repos = json.loads(f.read())
    
        repo_urls: List[str] = [repo["html_url"] for repo in repos]
        return repo_urls

    
if __name__ == "__main__":
    # # Crawl repo metadata and store into a file
    # Crawler.store_repo_metadata(Crawler.search_repo(), REPO_METADATA_STORAGE_URL)

    # Read repo url from a file
    repo_urls = Crawler.get_repo_html_url(REPO_METADATA_STORAGE_URL)

    # Check if repo name is unique accross searched repos' metadata
    repo_names = []
    tmp = 0
    for repo_url in repo_urls:
        tmp = repo_url.split('/')
        owner, repo = tmp[-2], tmp[-1]
        repo_names.append((owner, repo))

    repo_owner, repo_repo = zip(*repo_names)
    counter = Counter(repo_repo)
    
