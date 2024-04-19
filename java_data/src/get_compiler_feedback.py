import argparse
import re
import codecs
from functools import wraps
from subprocess import run
from time import time
from typing import Dict, List, NamedTuple, Optional
from make_data import get_functions, get_location

import pandas as pd
from tqdm import tqdm
import logging


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
    def __init__(self, df: pd.DataFrame, column_to_check: str, proj_storage_dir: str, tmp_dir: str, mvn: str, logger: logging.Logger):
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
        self.projects = set(df["proj_name"].to_list())
        self.mvn = mvn
        self.logger = logger
    
    def copy_project_to_tmp_dir(self):
        """Copy project to temporary directory
        """
        for project in tqdm(self.projects, desc="Copying project"):
            path_to_project = "{}/{}".format(self.proj_storage_dir, project)
            # if not os.path.exists("{}/{}".format(self.tmp_dir, project)):
            run(f"cp -rf {path_to_project} {self.tmp_dir}", shell=True)
    
    def _fill_file(self, row) -> Optional[str]:
        """Fill generated code to file
        Args:
            row (pd.core.series.Series): Row
            generated_func_column (str): Generated function column
            project_storage_url (str): Project storage url

        Returns:
            str: Filled generated code to file, if None, there is an error while filling file
        """
        absolute_file_path = "{}/{}/{}".format(
            self.proj_storage_dir, row["proj_name"], row["relative_path"]
        )
        with codecs.open(absolute_file_path, "r", encoding="utf-8", errors="ignore") as f:
            original_file = f.read().replace("\r\n", "\n")
        filled_class = row["masked_class"].replace(
            "<FILL_FUNCTION_BODY>", row[self.column_to_check]
        )
        # Find class in original file
        functions = get_functions(original_file)
        for function in functions:
            if (
                function["class_name"] == row["class_name"]
                and function["func_name"] == row["func_name"]
            ):
                class_start_idx, class_end_idx = get_location(
                    original_file, function["class_loc"]
                )
                filled_file = (
                    original_file[:class_start_idx]
                    + filled_class
                    + original_file[class_end_idx:]
                )
                return filled_file
        return None

    def modified_files(self):
        """Replace original file with file with generated code
        """
        for _, row in tqdm(df.iterrows(), desc="Modifying files", total=len(df)):
            path_to_file = "{}/{}/{}".format(self.tmp_dir, row["proj_name"], row["relative_path"])
            filled_file = self._fill_file(row)
            # If fail log file path into error file
            try:
                if not filled_file:
                    raise LookupError("There is an error while filling file {}".format(path_to_file))
                else:
                    with open(path_to_file, "w") as f:
                        f.write(row[self.column_to_check])
            except LookupError as e:
                self.logger.error(e)
            except:
                self.logger.error("Error while modifying file {}".format(path_to_file))

    def extract_error(self, compile_info: List[CompilerFeedback]) -> Dict[FileInfo, ErrorInfo]:
        """Extract error from feedback
        Args:
            compile_info (List[CompilerFeedback]): Compiler feedback
        Returns:
            Dict[FileInfo, ErrorInfo]: Error info
        """
        error_files: Dict[FileInfo, ErrorInfo] = {}
        err_pattern = r'^\[ERROR\] (?P<file>.+?):\[(?P<line>\d+),(?P<col>\d+)\] (?P<err>.+)$'
        for project_name, feedback  in compile_info:
            errors = set(re.findall(err_pattern, feedback, re.MULTILINE))
            for error in errors:
                file, line, col, err = error
                relative_path = file.split(project_name)[1][1:]
                file_error = f"""Line: {line}, Column: {col}, Error: {err})\n"""
                error_files[FileInfo(project_name=project_name, relative_path=relative_path)] = ErrorInfo(error_info=file_error)
        return error_files
    
    @timing       
    def add_compile_info(self) -> pd.DataFrame:
        """Add compile info to dataframe
        Returns:
            pd.DataFrame: Dataframe with compile info
        """
        compile_info: List[CompilerFeedback] = []
        for project in tqdm(self.projects, desc="Compiling project"):
            path_to_project = "{}/{}".format(self.tmp_dir, project)
            cmd = f"""
            cd {path_to_project}
            cd $(ls -d */|head -n 1)
            {self.mvn} clean compile
            """
            data = run(cmd, shell=True, capture_output=True, text=True)
            compile_info.append(CompilerFeedback(project, data.stdout))
        error_files = self.extract_error(compile_info)
        def get_compile_info(row):
            error = error_files.get(FileInfo(project_name=row["proj_name"], relative_path=row["relative_path"]), None)
            return error.error_info if error else "<COMPILED_SUCCESSFULLY>"
        df["compile_info"] = df.apply(get_compile_info, axis=1)
        return df
    
    def get_compilable_feedback(self):
        """Get compilable feedback
        """
        self.copy_project_to_tmp_dir()
        print("Copy projects to temp directory done")
        self.modified_files()
        print("Modify files done")
        new_df = self.add_compile_info()
        return new_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input")
    parser.add_argument("--input-type", dest="type")
    parser.add_argument("--output", dest="output")
    parser.add_argument("--dir", dest="dir")
    parser.add_argument("--tmp", dest="tmp")
    parser.add_argument("--col", dest="col")
    parser.add_argument("--mvn", dest="mvn")
    parser.add_argument("--logfile", dest="logfile")
    args = parser.parse_args()
    logging.basicConfig(filename=args.logfile,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S')
    logger = logging.getLogger("get_compilable_feedback")

    match args.type:
        case "jsonl":
            df = pd.read_json(args.input, lines=True)
        case "parquet":
            df = pd.read_parquet(args.input, "fastparquet")
        case "csv":
            df = pd.read_csv(args.input)
    print("Read input done")
    compiler_checker = CompilableChecker(df=df, 
                                         column_to_check=args.col, 
                                         proj_storage_dir=args.dir, 
                                         tmp_dir=args.tmp, 
                                         mvn=args.mvn,
                                         logger=logger)
    result = compiler_checker.get_compilable_feedback()
    print("Compilable rate: {:.2%}".format(len(result[result["compile_info"] == "<COMPILED_SUCCESSFULLY>"]) / len(result)))
    result.to_parquet(args.output, "fastparquet")



    
