import os
import argparse
import pandas as pd

base = os.path.dirname(os.path.abspath(__file__))


def initial(files_source: str, concurency: int, out: str):
    length = len(files_source)
    if length % concurency == 0:
        chunk = length // concurency
    else:
        chunk = length // concurency + 1

    files_source = pd.DataFrame(
        list(enumerate(files_source)), columns=["index", "source_code"]
    ).set_index("index")

    for i in range(1, concurency):
        files_source.iloc[(i - 1) * chunk : i * chunk].to_parquet(
            os.path.join(out, f"batch{i}.parquet"),
            engine="fastparquet",
        )
    files_source.iloc[(concurency - 1) * chunk :].to_parquet(
        os.path.join(out, f"batch{concurency}.parquet"),
        engine="fastparquet",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", dest="path")
    parser.add_argument("-c", "--concurency", dest="cc")
    parser.add_argument("-o", "--out", dest="out")
    args = parser.parse_args()
    files_source = pd.read_parquet(args.path, engine="fastparquet")[
        "source_code"
    ].tolist()
    initial(files_source, int(args.cc), args.out)
