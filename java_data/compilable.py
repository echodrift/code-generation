import argparse
import re
import requests
from collections import namedtuple, defaultdict
import pandas as pd
from tqdm import tqdm
from subprocess import run
import os
from functools import wraps
from time import time
from dataclasses import dataclass
from typing import Dict

HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}

@dataclass
class ProjectInfo:
    full_name: str
    created_at: str
    start: str


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result
    return wrap


def extract_error(compile_info: Dict[str, str]) -> List[FileError]:
    error_files = defaultdict(str)
    err_pattern = r'^\[ERROR\] (.+?):\[(?P<line>\d+),(?P<col>\d+)\] (?P<err>.+)$'
    compile_errors = []
    for repo_name in compile_info:
        errors = set(re.findall(pattern, compile_info[repo_name], re.MULTILINE))
        for error in errors:
            relative_path = error[0].split(repo_name)[1][1:]
            error_files[(repo_name, relative_path)] += "(Line: {}, Column: {}, Error: {})\n".format(error[1], error[2], error[3])
    return error_files
        
        
def copy_repo_to_tmp_dir(df: pd.DataFrame, column: str, proj_storage_url: str, tmp_dir: str,):
    # Copy repo into TEMPORARY DIRECTORY
    repos = list(set(df["proj_name"].to_list()))
    for _, row in tqdm(df.iterrows()):
        path_to_folder = "{}/{}".format(proj_storage_url, row["proj_name"])
        if not os.path.exists("{}/{}".format(tmp_dir, row["proj_name"])):
            run(f"cp -rf {path_to_folder} {tmp_dir}", shell=True)
        path_to_file = "{}/{}/{}".format(tmp_dir, row["proj_name"], row["relative_path"])
        # If fail log file path into error file
        try:
            with open(path_to_file, "w") as f:
                f.write(row[column])
        except:
            with open("./error.txt", "w") as f:
                f.write(path_to_file + '\n')

@timing       
def check_compilable(compile_info_storage_url: str):
    compile_infos = {}
    for repo in tqdm(repos):
        path_to_folder = "{}/{}".format(tmp_dir, repo)
        cmd = f"""
        cd {path_to_folder}
        cd $(ls -d */|head -n 1)
        /home/hieuvd/apache-maven-3.6.3/bin/mvn clean compile
        """
        data = run(cmd, shell=True, capture_output=True, text=True)
        compile_infos[repo] = data.stdout
        
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
    




    
