import argparse
import codecs
import logging
import re
from multiprocessing import Process, Queue
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


class Executor:
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
                new_file = Path(path_to_tmp_file)
                new_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with codecs.open(
                        path_to_tmp_file, "w", encoding="utf-8", errors="ignore"
                    ) as f:
                        f.write(original_file)
                except:
                    raise Exception("Can't write original file to tmp")
                try:
                    with codecs.open(
                        path_to_file, "w", encoding="utf-8", errors="ignore"
                    ) as f:
                        f.write(filled_file)
                except:
                    raise Exception("Can't write fill file to origin file")
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
            cmd = f"cp {path_to_tmp_file} {path_to_file}"
            run(cmd, shell=True)
        except:
            logging.error(
                "Error while return original file {}".format(path_to_file)
            )

    def get_compiler_feedback(self, row):
        path_to_project = "{}/{}".format(
            self.proj_storage_dir, row["proj_name"]
        )
        cmd = (
            f"cd {path_to_project} "
            "&& cd $(ls -d */|head -n 1) "
            "&& echo $(pwd)"
            f"&& {self.mvn} clean compile"
        )
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
                try:
                    compile_info = self.get_compiler_feedback(row)
                    errors = self.extract_error(compile_info)
                    compiler_feedback.append(errors)
                except:
                    logging.info(
                        "Can not get compiler feedback",
                        row["proj_name"] + "/" + row["relative_path"],
                    )
                    compiler_feedback.append("<execute_error>")
                finally:
                    self.return_original_file(row)
            else:
                logging.info(
                    "Can not modify file",
                    row["proj_name"] + "/" + row["relative_path"],
                )
                compiler_feedback.append("<execute_error>")
        return compiler_feedback


def group_dataframes(df_list, num_groups):
    """Group a list of DataFrames into a specified number of groups with roughly equal total rows.

    Args:
        df_list (List[pd.DataFrame]): List of DataFrames to be grouped.
        num_groups (int): Number of resulting groups.

    Returns:
        List[pd.DataFrame]: A list of grouped DataFrames.
    """
    # Calculate the total number of rows
    total_rows = sum(len(df) for df in df_list)

    # Calculate the approximate number of rows each group should have
    rows_per_group = total_rows // num_groups
    remainder = total_rows % num_groups

    # Initialize the groups
    groups = [[] for _ in range(num_groups)]
    group_sizes = [0] * num_groups

    # Sort DataFrames by size (optional, for better distribution)
    sorted_dfs = sorted(df_list, key=len, reverse=True)

    # Distribute DataFrames to groups
    for df in sorted_dfs:
        # Find the group with the smallest size
        min_group_index = group_sizes.index(min(group_sizes))

        # Add the DataFrame to this group
        groups[min_group_index].append(df)
        group_sizes[min_group_index] += len(df)

    # Concatenate the DataFrames within each group
    result_groups = [pd.concat(group, ignore_index=True) for group in groups]

    return result_groups


def process_dataframes_in_parallel(df_list, additional_args, process_dataframe):
    """
    Process multiple DataFrames in parallel.

    Args:
        df_list (list of pd.DataFrame): List of DataFrames to process.

    Returns:
        List of results from processing each DataFrame.
    """
    processes = []
    output_queue = Queue()

    # Create a process for each DataFrame
    for df in df_list:
        p = Process(
            target=process_dataframe, args=(df, additional_args, output_queue)
        )
        processes.append(p)
        p.start()

    # Collect the results
    results = []
    for _ in df_list:
        results.append(output_queue.get())

    # Ensure all processes have finished
    for p in processes:
        p.join()

    return results


def process_dataframe(df, additional_args, output_queue):
    """
    Process a DataFrame and put the result in the output queue.

    Args:
        df (pd.DataFrame): The DataFrame to process.
        output_queue (Queue): The queue to store the results.
    """
    print("A process is executing")
    (col, base_dir, tmp_dir, mvn) = additional_args
    # Example processing: here we just return the DataFrame size
    executor = Executor(df, col, base_dir, tmp_dir, mvn)
    df["compiler_feedback"] = executor.execute()
    output_queue.put(df)


def main(args):
    df = pd.read_parquet(args.input)
    proj_group = df.groupby(by="proj_name")
    dfs = [proj_group.get_group(x) for x in proj_group.groups]
    dfs = group_dataframes(dfs, 10)
    additional_args = (args.col, args.base_dir, args.tmp_dir, args.mvn)
    results = process_dataframes_in_parallel(
        dfs, additional_args, process_dataframe
    )
    final_result = pd.concat(results, axis=0)
    final_result.to_parquet(args.output)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
