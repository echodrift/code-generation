import argparse
import pandas as pd
import numpy as np
import subprocess
import shlex

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--num-batch", dest="num_batch", type=int)
parser.add_argument("--ds", dest="data_storage")
parser.add_argument("--os", dest="output_storage")


def main(args):
    dataset = pd.read_parquet(args.input)
    # Split dataset into pieces 
    batches = np.array_split(dataset, args.num_batch)
    for i, batch in enumerate(batches):
        batch.to_csv("{}/batch{}.csv".format(args.data_storage, i), index=False)
    print(f"Sharded dataset into {args.num_batch} batches")
    
    # Run parser
    for i in range(args.num_batch):
        cmd = (f"screen -dmS batch{i} bash -c "
        + "\"cd /var/data/lvdthieu/code-generation/java_data/extract_relevant_context/java-parser/target/classes "
        + "&& java -cp .:/var/data/.m2/org/apache/commons/commons-csv/1.11.0/commons-csv-1.11.0.jar:/var/data/.m2/commons-io/commons-io/2.16.1/commons-io-2.16.1.jar:/var/data/.m2/commons-codec/commons-codec/1.16.1/commons-codec-1.16.1.jar:/var/data/lvdthieu/code-generation/java_data/extract_relevant_context/java-parser/src/main/resources/Flute.jar:/var/data/.m2/me/tongfei/progressbar/0.10.0/progressbar-0.10.0.jar:/var/data/.m2/org/jline/jline/3.23.0/jline-3.23.0.jar "
        + "Main "
        + f"{args.data_storage}/batch{i}.csv "
        + "/var/data/lvdthieu/repos/processed-projects "
        + f"{args.output_storage}/batch{i}.csv\"")
        subprocess.run(cmd, shell=True)
        print(f"Created screen batch{i}")
        
    

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)