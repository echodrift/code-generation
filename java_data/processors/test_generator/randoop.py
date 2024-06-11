import logging
import os
import random
from argparse import ArgumentParser
from glob import glob
from multiprocessing import Pool
from subprocess import run
from typing import List

import pandas as pd
from tqdm import tqdm

random.seed(42)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def group_dataframes(dfs: List[pd.DataFrame], proc: int) -> List[pd.DataFrame]:
    """Group a list of DataFrames into a specified number of groups with roughly equal total rows.

    Args:
        dfs (List[pd.DataFrame]): List of DataFrames to be grouped.
        proc (int): Number of resulting groups.

    Returns:
        List[pd.DataFrame]: A list of grouped DataFrames.
    """
    # Initialize the groups
    groups = [[] for _ in range(proc)]
    group_sizes = [0] * proc

    # Sort DataFrames by size (optional, for better distribution)
    sorted_dfs = sorted(dfs, key=len, reverse=True)

    # Distribute DataFrames to groups
    for df in sorted_dfs:
        # Find the group with the smallest size
        min_group_index = group_sizes.index(min(group_sizes))

        # Add the DataFrame to this group
        groups[min_group_index].append(df)
        group_sizes[min_group_index] += len(df)

    result_groups = [pd.concat(group, ignore_index=True) for group in groups]
    return result_groups


def generate_test(args):
    (
        df,
        base_dir,
        time_limit,
        # output_limit,
        randoop,
        output_dir,
        log_dir,
        index,
    ) = args
    logger = logging.getLogger(f"logger{index}")
    logger.addHandler(logging.FileHandler(f"{log_dir}/logger{index}.log"))
    logger.setLevel(logging.ERROR)
    generate_status = []
    counter = 0
    for _, row in tqdm(
        df.iterrows(), total=len(df), desc=f"proc {index}", position=index
    ):
        counter += 1

        target_classes = (
            f"{base_dir}/{row['proj_name']}"
            f"/{row['relative_path'].split('/src/main/java/')[0]}/target/classes"
        )
        test_class = (
            row["relative_path"]
            .split("src/main/java/")[1]
            .replace(".java", "")
            .replace("/", ".")
        )
        test_package = ".".join(test_class.split(".")[:-1])
        target_dir = (
            f"{base_dir}/{row['proj_name']}"
            f"/{'_'.join(row['proj_name'].split('_')[1:])}/target"
        )
        if not os.path.exists(target_dir):
            jar = ""
        else:
            for item in os.listdir(target_dir):
                if item.endswith("jar-with-dependencies.jar"):
                    jar = f"{target_dir}/{item}"
                    break
            else:
                jar = ""
        junit_output_dir = (
            f"{output_dir}/{row['proj_name']}"
            f"/{row['relative_path'].replace('.java', '')}"
        )
        rev_path = "/".join(
            row["relative_path"].split("src/main/java/")[1].split("/")[:-1]
        )
        where_test = f"{junit_output_dir}/{rev_path}"
        cmd = (
            f"java -cp {target_classes}:{jar}:{randoop} randoop.main.Main gentests "
            f"--testclass={test_class} "
            f"--time-limit={time_limit} "
            # f"--output-limit={output_limit} "
            f"--junit-output-dir={junit_output_dir} "
            f"--junit-package-name={test_package} "
            f"--no-error-revealing-tests=true"
        )
        try:
            result = run(
                cmd, shell=True, text=True, capture_output=True, timeout=60
            )
            if result.returncode != 0 or not os.path.exists(where_test):
                logger.error(
                    f"Can not gen test for {row['proj_name']}/{row['relative_path']}"
                )
                generate_status.append(False)
            else:
                test_files = glob(f"{where_test}/*.java")
                for test_file in test_files:
                    with open(test_file, "r") as f:
                        if f".{row['func_name']}" in f.read():
                            generate_status.append(True)
                            logger.info(
                                f"Generated for {row['proj_name']}/{row['relative_path']}"
                            )
                            break
                else:
                    generate_status.append(False)
                    logger.error(
                        f"Can not find test for {row['proj_name']}/{row['relative_path']}"
                    )
        except Exception:
            generate_status.append(False)
            logger.error(
                f"Encounter exception for {row['proj_name']}/{row['relative_path']}"
            )

        if counter % 20 == 0:
            log_df = df.iloc[:counter]
            log_df["generate_status"] = generate_status
            log_df.to_parquet(f"{log_dir}/generate{index}.parquet")
    df["generate_status"] = generate_status
    return df


def main(args):
    df = pd.read_parquet(args.input)
    proj_group = df.groupby(by="proj_name")
    dfs = [proj_group.get_group(x) for x in proj_group.groups]
    dfs = group_dataframes(dfs, args.proc)
    additional_args = (
        args.base_dir,
        args.time_limit,
        # args.output_limit,
        args.randoop,
        args.output_dir,
        args.log_dir,
    )
    list_args = []
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir, exist_ok=True)
    for i in range(len(dfs)):
        list_args.append((dfs[i],) + additional_args + (i,))
    with Pool(args.proc) as p:
        results = p.map(generate_test, list_args)

    final_result = pd.concat(results, axis=0)
    final_result.to_parquet(args.output)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--input", dest="input")
    parser.add_argument("--output", dest="output")
    parser.add_argument("--base-dir", dest="base_dir")
    parser.add_argument("--time-limit", dest="time_limit", type=int)
    # parser.add_argument("--output-limit", dest="output_limit", type=int)
    parser.add_argument("--randoop", dest="randoop")
    parser.add_argument("--output-dir", dest="output_dir")
    parser.add_argument("--log-dir", dest="log_dir")
    parser.add_argument("--proc", dest="proc", type=int)
    args = parser.parse_args()
    main(args)
