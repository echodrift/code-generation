import argparse
import codecs
import logging
import re
from pathlib import Path
from subprocess import run
from typing import Optional, Tuple

import pandas as pd
from make_data.make_data import get_functions, get_location
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--output", dest="output")
parser.add_argument("--col", dest="col")
parser.add_argument("--base-dir", dest="base_dir")
parser.add_argument("--tmp-dir", dest="tmp_dir")
parser.add_argument("--mvn", dest="mvn")


class Excecutor:
    def __init__(
        self,
        df: pd.DataFrame,
        column_to_check: str,
        proj_storage_dir: str,
        tmp_dir: str,
        mvn: str,
    ):
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

    def fill_file(self, row) -> Optional[str]:
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
        with codecs.open(
            absolute_file_path, "r", encoding="utf-8", errors="ignore"
        ) as f:
            original_file = f.read().replace("\r\n", "\n")
        filled_class = row["masked_class"].replace(
            "<FILL_FUNCTION_BODY>", row[self.column_to_check]
        )
        # Find class in original file
        functions = get_functions(original_file)
        if functions:
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
                    return filled_file, original_file
            return None
        else:
            return None

    def modified_file(self, row) -> bool:
        """Replace original file with file with generated code"""
        path_to_file = "{}/{}/{}".format(
            self.proj_storage_dir, row["proj_name"], row["relative_path"]
        )
        path_to_tmp_file = "{}/{}/{}".format(
            self.tmp_dir, row["proj_name"], row["relative_path"]
        )
        res = self.fill_file(row)
        # If fail log file path into error file
        try:
            if not res:
                raise LookupError(
                    "There is an error while filling file {}".format(
                        path_to_file
                    )
                )
            else:
                filled_file, original_file = res
                with codecs.open(
                    path_to_file, "w", encoding="utf-8", errors="ignore"
                ) as f:
                    f.write(filled_file)

                new_file = Path(path_to_tmp_file)
                new_file.parent.mkdir(parents=True, exist_ok=True)
                with codecs.open(
                    path_to_tmp_file, "w", encoding="utf-8", errors="ignore"
                ) as f:
                    f.write(original_file)
        except LookupError as e:
            logging.error(e)
            return False
        except Exception as e:
            logging.error(e)
            logging.error("---------------------------------------------------")
            logging.error("Error while modifying file {}".format(path_to_file))
            return False
        return True

    def extract_error(self, compile_info):
        """Extract error from feedback
        Args:
            compile_info (List[CompilerFeedback]): Compiler feedback
        Returns:
            Dict[FileInfo, ErrorInfo]: Error info
        """
        err_pattern = r"^\[ERROR\] (?P<file>.+?):\[(?P<line>\d+),(?P<col>\d+)\] (?P<err>.+)$"
        file_errors = []
        errors = re.findall(err_pattern, compile_info, re.MULTILINE)
        for error in errors:
            file, line, col, err = error
            file_errors.append(
                f"""Line: {line}, Column: {col}, Error: {err})"""
            )
        return "\n".join(file_errors)

    def return_original_file(self, row):
        path_to_tmp_file = "{}/{}/{}".format(
            self.tmp_dir, row["proj_name"], row["relative_path"]
        )
        path_to_file = "{}/{}/{}".format(
            self.proj_storage_dir, row["proj_name"], row["relative_path"]
        )
        try:
            with open(path_to_tmp_file, "r") as f:
                original_file = f.read()
            with open(path_to_file, "w") as f:
                f.write(original_file)
        except:
            logging.error(
                "Error while return original file {}".format(path_to_file)
            )

    def get_compiler_feedback(self, row):
        path_to_project = "{}/{}".format(
            self.proj_storage_dir, row["proj_name"]
        )
        cmd = f"""
        cd {path_to_project}
        cd $(ls -d */|head -n 1)
        {self.mvn} clean compile
        """
        data = run(cmd, shell=True, capture_output=True, text=True)
        return data.stdout

    def execute_test(self, row):
        pass

    def execute(self):
        compiler_feedback = []
        for _, row in tqdm(
            self.df.iterrows(), desc="Executing", total=len(self.df)
        ):
            modified = self.modified_file(row)
            if modified:
                compile_info = self.get_compiler_feedback(row)
                errors = self.extract_error(compile_info)
                compiler_feedback.append(errors)
                self.return_original_file(row)
            else:
                logging.info(
                    "Can not modify file",
                    row["proj_name"] + "/" + row["relative_path"],
                )
                compiler_feedback.append("<execute_error>")
        return compiler_feedback


def main(args):
    df = pd.read_parquet(args.input)
    df = df.iloc[:5]
    print(df.info())
    executor = Excecutor(df, args.col, args.base_dir, args.tmp_dir, args.mvn)
    df["compiler_feedback"] = executor.execute()
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
