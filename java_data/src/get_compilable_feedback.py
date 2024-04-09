import argparse
import os
import re
from functools import wraps
from subprocess import run
from time import time
from typing import Dict, List, NamedTuple

import pandas as pd
from tqdm import tqdm

HEADERS = {
    'Authorization': '<GITHUB_TOKEN>', 
    'Accept': 'application/vnd.github.v3+json'
}
MVN = "/home/hieuvd/apache-maven-3.6.3/bin/mvn"

CompilerFeedback = NamedTuple("CompilerFeedback", [("project_name", str), ("feedback", str)])
FileInfo = NamedTuple("FileInfo", [("project_name", str), ("relative_path", str)])
ErrorInfo = NamedTuple("ErrorInfo", [("error_info", str)])


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


class CompilableChecker:
    def __init__(self, df: pd.DataFrame, column_to_check: str, proj_storage_dir: str, tmp_dir: str, output: str):
        """Constructor
        Args:
            df (pd.DataFrame): Dataframe of java code
            column_to_check (str): Column to check
            proj_storage_dir (str): Project storage directory
            tmp_dir (str): Temporary directory (to store a copy of project)
            output (str): Output
        """
        self.df = df
        self.column_to_check = column_to_check
        self.proj_storage_dir = proj_storage_dir
        self.tmp_dir = tmp_dir
        self.output = output
        self.projects = list(set(df["proj_name"].to_list()))
    
    def copy_project_to_tmp_dir(self):
        """Copy project to temporary directory
        """
        for project in self.projects:
            path_to_project = "{}/{}".format(self.proj_storage_dir, project)
            if not os.path.exists("{}/{}".format(self.tmp_dir, project)):
                run(f"cp -rf {path_to_project} {self.tmp_dir}", shell=True)
    
    def modified_files(self):
        """Replace original file with file with generated code
        """
        for _, row in tqdm(df.iterrows()):
            path_to_file = "{}/{}/{}".format(self.tmp_dir, row["proj_name"], row["relative_path"])
            # If fail log file path into error file
            try:
                with open(path_to_file, "w") as f:
                    f.write(row[self.column_to_check])
            except:
                with open("./error.txt", "w") as f:
                    f.write(path_to_file + '\n')

    def extract_error(self, compile_info: List[CompilerFeedback]) -> Dict[FileInfo, ErrorInfo]:
        """Extract error from feedback
        Args:
            compile_info (List[CompilerFeedback]): Compiler feedback
        Returns:
            Dict[FileInfo, ErrorInfo]: Error info
        """
        error_files: Dict[FileInfo, ErrorInfo] = {}
        err_pattern = r'^\[ERROR\] (.+?):\[(?P<line>\d+),(?P<col>\d+)\] (?P<err>.+)$'
        for project_name, feedback  in compile_info:
            errors = set(re.findall(err_pattern, feedback, re.MULTILINE))
            for error in errors:
                relative_path = error[0].split(project_name)[1][1:]
                file_error = f"""(Line: {error["line"]}, Column: {error["col"]}, Error: {error["err"]})\n"""
                error_files[FileInfo(project_name, relative_path)] = ErrorInfo(file_error)
        return error_files
    
    @timing       
    def add_compile_info(self) -> pd.DataFrame:
        """Add compile info to dataframe
        Returns:
            pd.DataFrame: Dataframe with compile info
        """
        compile_info: List[CompilerFeedback] = []
        for project in tqdm(self.projects):
            path_to_project = "{}/{}".format(self.tmp_dir, project)
            cmd = f"""
            cd {path_to_project}
            cd $(ls -d */|head -n 1)
            {MVN} clean compile
            """
            data = run(cmd, shell=True, capture_output=True, text=True)
            compile_info.append(CompilerFeedback(project, data.stdout))
        error_files = self.extract_error(compile_info)
        def get_compile_info(row):
            error = error_files[(row["proj_name"], row["relative_path"])]
            return error if error else "<COMPILED_SUCCESSFULLY>"
        df["compile_info_" + self.column_to_check] = df.apply(get_compile_info, axis=1)
        return df
    
    
    def get_compilable_feedback(self):
        """Get compilable feedback
        """
        if os.path.exists(self.output):
            os.remove(self.output)
        self.copy_project_to_tmp_dir()
        self.modified_files()
        new_df = self.add_compile_info()
        new_df.to_parquet(self.output, "fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-d", "--dir", dest="dir")
    parser.add_argument("-t", "--tmp", dest="tmp")
    parser.add_argument("--col", dest="col")
    args = parser.parse_args()
    
    df = pd.read_parquet(args.input, "fastparquet")
    CompilableChecker(df, args.col, args.dir, args.tmp, args.output).get_compilable_feedback()



    
