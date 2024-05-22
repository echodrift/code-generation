import logging
import os
import random
from argparse import ArgumentParser
from subprocess import run
from typing import List

import pandas as pd
from tqdm import tqdm

random.seed(42)
parser = ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--base-dir", dest="base_dir")
parser.add_argument("--time-limit", dest="time_limit", type=int)
parser.add_argument("--output-limit", dest="output_limit", type=int)
parser.add_argument("--output", dest="output")
parser.add_argument("--randoop", dest="randoop")
parser.add_argument("--start", dest="start", type=int)
parser.add_argument("--end", dest="end", type=int)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def search_jar_in_project(project_url: str) -> List[str]:
    all_jars = []
    for root, dirs, files in os.walk(project_url):
        for file in files:
            if file.endswith(".jar"):
                all_jars.append(os.path.join(root, file))
    if len(all_jars) > 42:
        all_jars = random.sample(all_jars, 42)
    return all_jars


def _generate_test(args) -> bool:
    # generate_status = []
    # for item in args:
    # print(args)
    (
        base_dir,
        proj_name,
        relative_path,
        # method_qualified_name,
        randoop_class_path,
        time_limit,
        output_limit,
    ) = args

    relative_path_to_pom = relative_path.split("/src/main/java/")[0]
    path_to_pom = f"{base_dir}/{proj_name}/{relative_path_to_pom}"
    test_path = f'{base_dir}/../randoop/{proj_name}/{relative_path.replace(".java", "")}'
    # result_path = relative_path.split("src/main/java/")[1].replace(".java", "")
    if os.path.exists(
        # f"{path_to_pom}/randoop/{result_path}/RegressionTest.java"
        f"{test_path}/RegressionTest.java"
    ) or os.path.exists(f"{test_path}/RegressionTest0.java"):
        print("File existed")
        return True

    qualified_name = (
        relative_path.split("src/main/java/")[1]
        .replace(".java", "")
        .replace("/", ".")
    )
    all_local_jars = search_jar_in_project(f"{base_dir}/{proj_name}")
    # print(*all_local_jars, sep='\n')
    class_path = (
        "."
        f":{path_to_pom}/target/classes"
        f":{':'.join(all_local_jars)}"
        f":{randoop_class_path}"
    )
    cmd = (
        f"cd {path_to_pom} "
        # f"&& echo \"{qualified_name + '.' + method_qualified_name}\" > methodlist.txt "
        f"&& timeout {time_limit} java -classpath {class_path} randoop.main.Main gentests "
        f"--testclass={qualified_name} "
        # f"--methodlist=methodlist.txt "
        f"--time-limit={time_limit} "
        f"--output-limit={output_limit} "
        f"--junit-output-dir={test_path} "
        f"--no-error-revealing-tests=true"
        # f"--progressdisplay=false "
        # f"|| timeout {time_limit} java -classpath {class_path} randoop.main.Main gentests "
        # f"--testclass={qualified_name} "
        # f"--time-limit={time_limit} "
        # f"--output-limit={output_limit} "
        # f"--junit-output-dir={result_path} "
        # f"--testsperfile=1 "
        # f"--progressdisplay=false "
    )
    data = ""
    try:
        data = run(cmd, shell=True, text=True)
    except Exception:
        print(data.err)
        # generate_status.append(False)
        return False
        # logging.info(
        #     f"Can not gentest for {row['proj_name']}/{row['relative_path']}"
        # )
    # else:
    return os.path.exists(f"{test_path}/RegressionTest.java")


def generate_test(
    dataset: pd.DataFrame,
    base_dir: str,
    time_limit: int,
    output_limit: int,
    randoop_path: str,
) -> pd.Series:
    # def method_signature(method_qualified_name):
    #     method_signature_pattern = re.compile(
    #         r"(\w+\s+)*(\w+\.)*(\w+)\(([^)]*)\)"
    #     )
    #     match = method_signature_pattern.search(method_qualified_name)
    #     if match:
    #         method_name = match.group(3)
    #         parameters = match.group(4)
    #         method_signature = f"{method_name}({parameters})"
    #         return method_signature
    #     else:
    #         return "<can_not_resolved>"

    # method_qualified_name = list(
    #     map(
    #         lambda tmp: method_signature(tmp),
    #         dataset["method_qualified_name"].tolist(),
    #     )
    # )
    # iteration = len(dataset)
    # arguments = list(
    #     zip(
    #         [base_dir] * iteration,
    #         dataset["proj_name"],
    #         dataset["relative_path"],
    #         # method_qualified_name,
    #         [randoop_class_path] * iteration,
    #         [time_limit] * iteration,
    #         [output_limit] * iteration,
    #     )
    # )
    # generate_status = map_with_multiprocessing_pool(
    #     function=_generate_test,
    #     iterable=arguments,
    #     num_proc=10,
    #     batched=False,
    #     disable_tqdm=False,
    #     desc="Generating test",
    #     batch_size=-1,
    #     types=tuple,
    # )

    generate_status = []

    for _, row in tqdm(
        dataset.iterrows(), desc="Generating test", total=len(dataset)
    ):
        # try:
        generate_status.append(
            _generate_test(
                (
                    base_dir,
                    row["proj_name"],
                    row["relative_path"],
                    # method_qualified_name[idx],
                    randoop_path,
                    time_limit,
                    output_limit,
                )
            )
        )

        # except Exception:
        #     generate_status.append(False)

    dataset["generate_status"] = generate_status
    return dataset


def main(args):
    df = pd.read_parquet(args.input)
    df = df.iloc[args.start : args.end]
    generate_status = generate_test(
        df, args.base_dir, args.time_limit, args.output_limit, args.randoop
    )
    generate_status.to_parquet(args.output)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
