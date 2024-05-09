import logging
import os
from argparse import ArgumentParser
from subprocess import run

import pandas as pd

parser = ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--base-dir", dest="base_dir")
parser.add_argument("--time-limit", dest="time_limit")
parser.add_argument("--output-limit", dest="output_limit")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def main(args):
    df = pd.read_parquet(args.input)
    df = df.sample(n=5, random_state=0)
    df.to_csv("/var/data/lvdthieu/test.csv")
    randoop_class_path = f"{BASE_DIR}/lib/randoop-4.3.3/randoop-all-4.3.3.jar"
    junit_class_path = (
        f"{BASE_DIR}/lib/hamcrest-core-1.3.jar" 
        f":{BASE_DIR}/lib/junit-4.12.jar"
    )
    for _, row in df.iterrows():
        relative_path_to_pom = row["relative_path"].split("/src/main/java/")[0]
        path_to_pom = f"{args.base_dir}/{row["proj_name"]}/{relative_path_to_pom}"
        qualified_name = (
            row["relative_path"]
            .split("src/main/java/")[1]
            .replace(".java", "")
            .replace("/", ".")
        )
        # if row["proj_name"] == "vsch_flexmark-java":  # Temporary add
        class_path = (
            "."
            f":{path_to_pom}/target/classes"
            f":{path_to_pom}/target/dependency/*"
            f":{randoop_class_path}"
        )
        cmd = (
            f"cd {path_to_pom} "
            f"&& java -classpath {class_path} randoop.main.Main gentests "
            f"--testclass {qualified_name} "
            f"--methodlist={path_to_pom}/methodlist.txt "
            f"--time-limit {args.time_limit}"
            f"--output-limit {args.output_limit}"
        )
        # print(cmd)
        try:
            run(cmd, shell=True)
        except Exception:
            logging.info(
                f"Can not gentest for {row["proj_name"]}/{row["relative_path"]}"
            )
        break


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
