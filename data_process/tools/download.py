import pandas as pd
from datasets import load_dataset
import argparse


def download_data(dataset: str, split: str, store_dir: str):
    """This function aims to download data from huggingface platform

    Args:
        dataset (str): Dataset name (<user>/<dataset> format)
        split (str): Choose option in ["train", "test"]
        store_dir (str): Directory path to store dataset
    """
    data = load_dataset(dataset, split=split)
    data = pd.DataFrame(data)
    data.to_parquet(f"{store_dir}/{'_'.join(dataset.split('/'))}", engine="fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dataset", dest="dataset")
    parser.add_argument("-s", "--split", dest="split")
    parser.add_argument("-o", "--out", dest="out")
    args = parser.parse_args()
    download_data(args.dataset, args.split, args.out)
