import argparse
import os
from multiprocessing import Pool, cpu_count
from subprocess import run

import numpy as np
import pandas as pd
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="input")
# parser.add_argument("--num-batch", dest="num_batch", type=int)
parser.add_argument("--parser", dest="parser")
parser.add_argument("--base-dir", dest="base_dir")
parser.add_argument("--output", dest="output")
parser.add_argument("--proc", dest="proc")
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


# Define the processing function
def process_chunk(args):
    # Example processing function
    # Replace this with your actual processing logic
    # class_path = (
    #     "."
    #     f":'/var/data/lvdthieu/code-generation/java_data/processors/java_parser/target/dependency/*'"
    #     # f":{args.parser}/src/main/resources/Flute.jar"
    # )
    (index, df_chunk, class_path) = args
    relevant_context = []
    for _, row in tqdm(df_chunk.iterrows(), total=len(df_chunk), position=index, desc=f"proc {index}"):
        cmd = (
            # f'screen -dmS batch{i} bash -c "'
            # f"cd {args.parser}/target/classes "
            # f"&& java -cp {class_path} "
            # "Main "
            # f"{BASE_DIR}/data/batch{i}.csv "
            # f"{args.base_dir} "
            # f'{BASE_DIR}/out/batch{i}.csv"'
            f"cd {args.parser}/target/classes "
            f"&& java -cp {class_path} "
            "Main "
            f"{args.base_dir} "
            f"{row['proj_name']} "
            f"{row['relative_path']}"
        )
        try:
            data = run(cmd, shell=True, text=True, capture_output=True)
            relevant_context.append(data.stdout)
        except:
            relevant_context.append("<encounter_error>")
    df_chunk["relevant_context"] = relevant_context
    return df_chunk


# Helper function to parallelize DataFrame processing
def parallelize_dataframe(df, func, class_path, num_partitions=None):
    if num_partitions is None:
        num_partitions = cpu_count()
    df_split = np.array_split(df, num_partitions)

    with Pool(num_partitions) as pool:
        tasks = [(index, df_chunk, class_path) for index, df_chunk in enumerate(df_split)]
        results = pool.map(func, tasks)

    df = pd.concat(results)
    return df


def main(args):
    dataset = pd.read_parquet(args.input)
    # dataset = dataset.iloc[:100]
    # Split dataset into pieces
    # batches = np.array_split(dataset, args.num_batch)
    # for i, batch in enumerate(batches):
    # batch.to_csv(f"{BASE_DIR}/data/batch{i}.csv", index=False)
    # print(f"Sharded dataset into {args.num_batch} batches")

    class_path = (
        "."
        f":'{args.parser}/target/dependency/*'"
        # f":{args.parser}/src/main/resources/Flute.jar"
    )
    dataset = parallelize_dataframe(dataset, process_chunk, class_path, args.proc)
    dataset.to_csv(args.output)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
