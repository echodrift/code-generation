import os
from argparse import ArgumentParser
from subprocess import run
from typing import List

import numpy as np
import pandas as pd
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--base-dir", dest="base_dir")
parser.add_argument("--task", dest="task")
parser.add_argument("--parser", dest="parser")
parser.add_argument("--num-batch", dest="num_batch", type=int)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def extract_maven_dir_urls(dataset: pd.DataFrame, base_dir: str) -> List[str]:
    paths = []
    for _, row in dataset.iterrows():
        relative_path_to_classes = row["relative_path"].split("/src/main/java/")[0]
        path_to_mvn_dir = (
            f"""{base_dir}/{row["proj_name"]}/{relative_path_to_classes}"""
        )
        paths.append(path_to_mvn_dir)
    return paths


def maven_config(urls: List[str]):
    for url in tqdm(urls, desc="Config maven"):
        cmd = f"cd {url} " + "&& mvn dependency:copy-dependencies"
        try:
            run(cmd, shell=True)
        except:
            pass


def extract_method_qualified_name(
    dataset: pd.DataFrame, num_batch: int, parser: str, base_dir: str
):
    # Split dataset into pieces
    batches = np.array_split(dataset, num_batch)
    for i, batch in enumerate(batches):
        batch.to_csv(f"{BASE_DIR}/data/batch{i}.csv", index=False)
    print(f"Sharded dataset into {num_batch} batches")

    class_path = (
        "." f":'{parser}/target/dependency/*'" f":{parser}/src/main/resources/Flute.jar"
    )
    # Run parser
    for i in range(num_batch):
        cmd = (
            f'screen -dmS batch{i} bash -c "'
            f"cd {parser}/target/classes "
            f"&& java -cp {class_path} "
            "Main "
            f"{BASE_DIR}/data/batch{i}.csv "
            f"{base_dir} "
            f"{BASE_DIR}/out/batch{i}.csv "
            "'<method_qualified_names>'\""
        )
        # print(cmd)
        # break
        run(cmd, shell=True)
        print(f"Created screen batch{i}")


def main(args):
    df = pd.read_parquet(args.input)
    if args.task == "config-maven":
        path_to_mvn_dirs = extract_maven_dir_urls(df, args.base_dir)
        maven_config(path_to_mvn_dirs)

    elif args.task == "extract-method-qualified-name":
        extract_method_qualified_name(df, args.num_batch, args.parser, args.base_dir)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
