import argparse

import pandas as pd
import logging

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--output", des="output")



def main(args):
    df = pd.read_parquet(args.input)
    

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
