import argparse
import os
import subprocess

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--num-batch", dest="num_batch", type=int)
parser.add_argument("--parser", dest="parser")
parser.add_argument("--base-dir", dest="base_dir")
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def main(args):
    dataset = pd.read_parquet(args.input)
    # Split dataset into pieces
    batches = np.array_split(dataset, args.num_batch)
    for i, batch in enumerate(batches):
        batch.to_csv(f"{BASE_DIR}/data/batch{i}.csv", index=False)
    print(f"Sharded dataset into {args.num_batch} batches")

    class_path = (
        "."
        f":'{args.parser}/target/dependency/*'"
        f":{args.parser}/src/main/resources/Flute.jar"
    )
    # Run parser
    for i in range(args.num_batch):
        cmd = (
            f'screen -dmS batch{i} bash -c "'
            f"cd {args.parser}/target/classes "
            f"&& java -cp {class_path} "
            "Main "
            f"{BASE_DIR}/data/batch{i}.csv "
            f"{args.base_dir} "
            f"{BASE_DIR}/out/batch{i}.csv "
            '\<inherit_elements\>"'
        )
        subprocess.run(cmd, shell=True)
        print(f"Created screen batch{i}")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
