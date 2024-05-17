import argparse

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument()


def main(args):
    df = pd.read_parquet(args.input)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
