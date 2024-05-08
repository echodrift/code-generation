from argparse import ArgumentParser
from typing import List
from subprocess import run
import pandas as pd
from tqdm import tqdm


parser = ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--base-dir", dest="base_dir")


def extract_maven_dir_urls(dataset: pd.DataFrame, base_dir: str) -> List[str]:
    paths = []
    for _, row in dataset.iterrows():
        relative_path_to_classes = row["relative_path"].split("/src/main/java/")[0]
        path_to_mvn_dir = f"""{base_dir}/{row["proj_name"]}/{relative_path_to_classes}"""
        paths.append(path_to_mvn_dir)
    return paths


def maven_config(urls: List[str]):
    for url in tqdm(urls, desc="Config maven"):
        cmd = (f"cd {url} "
               + "&& mvn dependency:copy-dependencies")
        try:
            run(cmd, shell=True)
        except:
            pass

def main(args):
    df = pd.read_parquet(args.input)
    path_to_mvn_dirs = extract_maven_dir_urls(df, args.base_dir)
    maven_config(path_to_mvn_dirs)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)