import os
import argparse
import pandas as pd

base = os.path.dirname(os.path.abspath(__file__))


def merging(files_source: str, concurency: int, out: str):
    dfs = []
    for i in range(1, concurency + 1):
        dfs.append(
            pd.read_parquet(
                os.path.join(files_source, f"result{i}.parquet"), engine="fastparquet"
            )
        )
    result = pd.concat(dfs, axis=0).reset_index(drop=True)
    result.to_parquet(out, engine="fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-c", "--concurency", dest="cc")
    parser.add_argument("-o", "--output", dest="out")
    args = parser.parse_args()
    merging(args.input, int(args.cc), args.out)
