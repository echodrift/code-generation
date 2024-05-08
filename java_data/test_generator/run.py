import pandas as pd
from argparse import ArgumentParser
from subprocess import run
import logging
import os

parser = ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--base-dir", dest="base_dir")
parser.add_argument("--time-limit", dest="time_limit")
parser.add_argument("--output-limit", dest="output_limit")

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def main(args):
    df = pd.read_parquet(args.input)
    df = df.sample(n=5, random_state=0)
    df.to_csv("/var/data/lvdthieu/test.csv")    

    for _, row in df.iterrows():
        relative_path_to_classes = row["relative_path"].split("/src/main/java/")[0]
        path_to_classes = f"""{args.base_dir}/{row["proj_name"]}/{relative_path_to_classes}""" 
        qualified_name = row["relative_path"].split("src/main/java/")[1].replace(".java", "").replace('/', '.')
        if row["proj_name"] == "vsch_flexmark-java":  # Temporary add
            cmd = (f"export RANDOOP={BASE_DIR}/lib/randoop-4.3.3/randoop-all-4.3.3.jar "
                + f"&& export JUNIT={BASE_DIR}/lib/hamcrest-core-1.3.jar:{BASE_DIR}/lib/junit-4.12.jar "
                + f"&& cd {path_to_classes} "
                + f"&& java -classpath .:{path_to_classes}/target/classes:{path_to_classes}/target/dependency/*:$RANDOOP randoop.main.Main gentests --testclass {qualified_name} --methodlist={path_to_classes}/methodlist.txt --output-limit=100 --time-limit {args.time_limit} --output-limit {args.output_limit}")
        # print(cmd)
            try:
                run(cmd, shell=True)
            except Exception:
                logging.info(f"""Can not gentest for {row["proj_name"]}/{row["relative_path"]}""")
            break
    

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)