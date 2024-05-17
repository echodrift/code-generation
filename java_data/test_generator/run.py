import logging
import multiprocessing as mp
import os
from argparse import ArgumentParser
from subprocess import run
from typing import List, Tuple

import pandas as pd
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--base-dir", dest="base_dir")
parser.add_argument("--time-limit", dest="time_limit", type=int)
parser.add_argument("--output-limit", dest="output_limit", type=int)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def search_jar_in_project(project_url: str) -> List[str]:
    all_jars = []
    for root, dirs, files in os.walk(project_url):
        for file in files:
            if file.endswith(".jar"):
                all_jars.append(os.path.join(root, file))
    return all_jars


def generate_test_case_a_file(args: Tuple[str, str, str]) -> bool:
    (
        base_dir,
        proj_name,
        relative_path,
        randoop_class_path,
        time_limit,
        output_limit,
    ) = args
    # if row["proj_name"] == "soot-oss_soot":  # Temporary add
    relative_path_to_pom = relative_path.split("/src/main/java/")[0]
    path_to_pom = f"{base_dir}/{proj_name}/{relative_path_to_pom}"
    qualified_name = (
        relative_path.split("src/main/java/")[1]
        .replace(".java", "")
        .replace("/", ".")
    )
    result_path = relative_path.split("src/main/java/")[1].replace(".java", "")
    all_local_jars = search_jar_in_project(f"{base_dir}/{proj_name}")
    # print(*all_local_jars, sep='\n')
    class_path = (
        "."
        f":{path_to_pom}/target/classes"
        f":{':'.join(all_local_jars)}"
        f":{randoop_class_path}"
    )
    cmd = (
        f"cd {path_to_pom} "
        f"&& timeout 20 java -classpath {class_path} randoop.main.Main gentests "
        f"--testclass {qualified_name} "
        # f"--methodlist={path_to_pom}/methodlist.txt "
        f"--time-limit {time_limit} "
        f"--output-limit {output_limit} "
        f"--junit-output-dir {result_path}"
    )
    # print(cmd)
    try:
        run(cmd, shell=True)
    except Exception:
        return False
        # logging.info(
        #     f"Can not gentest for {row['proj_name']}/{row['relative_path']}"
        # )
    return True


def generate_test_cases(
    dataset: pd.DataFrame, base_dir: str, time_limit: int, output_limit: int
) -> pd.Series:
    randoop_class_path = f"{BASE_DIR}/lib/randoop-4.3.3/randoop-all-4.3.3.jar"
    # iteration = len(dataset)
    # arguments = zip(
    #     [base_dir] * iteration,
    #     dataset["proj_name"],
    #     dataset["relative_path"],
    #     [randoop_class_path] * iteration,
    #     [time_limit] * iteration,
    #     [output_limit] * iteration,
    # )
    # with mp.Pool(processes=10) as pool:
    #     rows = list(
    #         tqdm(
    #             pool.imap(generate_test_case_a_file, arguments),
    #             total=iteration,
    #             desc="Generating test",
    #         )
    #     )
    generate_status = []
    for _, row in tqdm(
        dataset.iterrows(), desc="Generating test", total=len(dataset)
    ):
        try:
            generate_status.append(
                generate_test_case_a_file(
                    base_dir,
                    row["proj_name"],
                    row["relative_path"],
                    randoop_class_path,
                    time_limit,
                    output_limit,
                )
            )
        except:
            generate_status.append(False)

    dataset["generated_test"] = generate_status

    return dataset


def main(args):
    df = pd.read_parquet(args.input)
    df = df.loc[20000:]
    generate_status = generate_test_cases(
        df, args.base_dir, args.time_limit, args.output_limit
    )
    generate_status.to_parquet("/var/data/lvdthieu/generate_status_5.parquet")
    # junit_class_path = (
    #     f"{BASE_DIR}/lib/hamcrest-core-1.3.jar"
    #     f":{BASE_DIR}/lib/junit-4.12.jar"
    # )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
