import argparse
import re
import requests
from collections import Counter, namedtuple, defaultdict
import pandas as pd
from tqdm import tqdm
from subprocess import run
import os

PROJ_INFO = namedtuple("PROJ_INFO", "full_name created_at star")
HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}


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
            proj_infos.append(PROJ_INFO(full_name=response["full_name"], 
                                    created_at=response["created_at"], 
                                    star=response["stargazers_count"]))
        except:
            with open("error.txt", "a") as f:
                f.write(proj_url + '\n')
    return pd.DataFrame(proj_infos)


def extract_error(compile_infos: dict) -> defaultdict:
    error_files = defaultdict(str)
    pattern = r'^\[ERROR\] (.+?):\[(\d+),(\d+)\] (.+)$'
    compile_errors = []
    for proj_name in compile_infos:
        errors = set(re.findall(pattern, compile_infos[proj_name], re.MULTILINE))
        for error in errors:
            relative_path = error[0].split(proj_name)[1][1:]
            error_files[(proj_name, relative_path)] += "(Line: {}, Column: {}, Error: {})\n".format(error[1], error[2], error[3])
    return error_files
         
        
def check_compilable(df: pd.DataFrame, column: str, proj_storage_url: str, tmp_dir_url: str, compile_info_storage_url: str):
    projects = list(set(df["proj_name"].to_list()))
    run(f"rm -rf {tmp_dir_url}/*", shell=True)
    # run(["rm", "-rf", f"{tmp_dir_url}/*/"])
    for _, row in tqdm(df.iterrows()):
        path_to_folder = "{}/{}".format(proj_storage_url, row["proj_name"])
        if not os.path.exists("{}/{}".format(tmp_dir_url, row["proj_name"])):
            run(f"cp -rf {path_to_folder} {tmp_dir_url}", shell=True)
        path_to_file = "{}/{}/{}".format(tmp_dir_url, row["proj_name"], row["relative_path"])
        try:
            with open(path_to_file, "w") as f:
                f.write(row[column])
        except:
            with open("./error.txt", "w") as f:
                f.write(path_to_file + '\n')

    compile_infos = {}
    for project in tqdm(projects):
        path_to_project = "{}/{}".format(tmp_dir_url, project)
        cmd = f"""
        cd {path_to_project}
        cd $(ls -d */|head -n 1)
        /home/hieuvd/apache-maven-3.6.3/bin/mvn clean compile
        """
        data = run(cmd, shell=True, capture_output=True, text=True)
        compile_infos[project] = data.stdout
        
    error_files = extract_error(compile_infos)
    def compile_info(row):
        error = error_files[(row["proj_name"], row["relative_path"])]
        return error if error else "<COMPILED_SUCCESSFULLY>"
    df["compile_info_" + column] = df.apply(compile_info, axis=1)
    df.to_parquet(compile_info_storage_url, "fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-d", "--dir", dest="dir")
    parser.add_argument("-t", "--tmp", dest="tmp")
    parser.add_argument("--col", dest="col")
    args = parser.parse_args()
    df = pd.read_parquet(args.input, "fastparquet")
    check_compilable(df, args.col, args.dir, args.tmp, args.output)
    




    
