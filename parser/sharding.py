import os
import argparse
import pandas as pd

base = os.path.dirname(os.path.abspath(__file__))


def sharding(input: str, concurency: int, output: str):
    files_source = pd.read_parquet(input, engine="fastparquet")["source_code"].tolist()
    length = len(files_source)
    if length % concurency == 0:
        chunk = length // concurency
    else:
        chunk = length // concurency + 1

    files_source = pd.DataFrame(
        list(enumerate(files_source)), columns=["index", "source_code"]
    ).set_index("index")
    
    files_source["source_idx"] = files_source.index

    for i in range(1, concurency):
        files_source.iloc[(i - 1) * chunk : i * chunk].to_parquet(
            os.path.join(output, f"batch{i}.parquet"),
            engine="fastparquet",
        )
    files_source.iloc[(concurency - 1) * chunk :].to_parquet(
        os.path.join(output, f"batch{concurency}.parquet"),
        engine="fastparquet",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-c", "--concurency", dest="cc")
    parser.add_argument("-o", "--output", dest="out")
    args = parser.parse_args()

    sharding(args.input, int(args.cc), args.out)
