import os
import argparse
import pandas as pd

base = os.path.dirname(os.path.abspath(__file__))


def sharding(input: str, concurrency: int, output: str):
    """This function aims to split large parquet file into multiple small parquet files

    Args:
        input (str): Large parquet file path
        concurrency (int): Number of small files want to split
        output (str): Directory to store result
    """
    files_source = pd.read_parquet(input, engine="fastparquet").reset_index(drop=True)
    length = len(files_source)
    if length % concurrency == 0:
        chunk = length // concurrency
    else:
        chunk = length // concurrency + 1

    # files_source = pd.DataFrame(
    #     list(enumerate(files_source)), columns=["index", "source_code"]
    # ).set_index("index")

    files_source["source_idx"] = files_source.index

    for i in range(1, concurrency):
        files_source.iloc[(i - 1) * chunk : i * chunk].to_parquet(
            os.path.join(output, f"batch{i}.parquet"),
            engine="fastparquet",
        )
    files_source.iloc[(concurrency - 1) * chunk :].to_parquet(
        os.path.join(output, f"batch{concurrency}.parquet"),
        engine="fastparquet",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-c", "--concurrency", dest="cc")
    parser.add_argument("-o", "--output", dest="out")
    args = parser.parse_args()

    sharding(args.input, int(args.cc), args.out)
