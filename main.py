import json
import os
from typing import List

import pandas as pd
from datasets import load_dataset
from subprocess import run, check_output
import re

ERROR = [
    "ParserError",
    "DocstringParsingError",
    "SyntaxError",
    "DeclarationError",
    "TypeError",
    "UnimplementedFeatureError",
]


def make_solidity_file_data():
    train_file = load_dataset("andstor/smart_contracts", split="train")
    test_file = load_dataset("andstor/smart_contracts", split="test")
    valid_file = load_dataset("andstor/smart_contracts", split="validation")

    train_file = pd.DataFrame(train_file)
    # print(train_file.info())

    test_file = pd.DataFrame(test_file)
    # print(test_file.info())

    valid_file = pd.DataFrame(valid_file)
    # print(valid_file.info())

    train_file = train_file[
        [
            "contract_name",
            "contract_address",
            "source_code",
            "compiler_version",
            "language",
        ]
    ]
    test_file = test_file[
        [
            "contract_name",
            "contract_address",
            "source_code",
            "compiler_version",
            "language",
        ]
    ]
    valid_file = valid_file[
        [
            "contract_name",
            "contract_address",
            "source_code",
            "compiler_version",
            "language",
        ]
    ]

    train_file = pd.concat([train_file, valid_file], axis=0).reset_index(drop=True)
    train_file = train_file.rename(
        columns={
            "contract_name": "file_name",
            "contract_address": "file_address",
        }
    )
    test_file = test_file.rename(
        columns={
            "contract_name": "file_name",
            "contract_address": "file_address",
        }
    )
    train_file = train_file[train_file["language"] == "Solidity"]
    test_file = test_file[test_file["language"] == "Solidity"]
    train_file.reset_index(drop=True, inplace=True)
    test_file.reset_index(drop=True, inplace=True)
    train_file = train_file.drop(columns=["language"])
    test_file = test_file.drop(columns=["language"])
    train_file.to_parquet("./data/solfile/train_file.parquet", engine="fastparquet")
    test_file.to_parquet("./data/solfile/test_file.parquet", engine="fastparquet")


def download_data():
    train_data = load_dataset("lvdthieu/codegen", split="train")
    test_data = load_dataset("lvdthieu/codegen", split="test")
    train_data = pd.DataFrame(train_data)
    test_data = pd.DataFrame(test_data)
    train_data.to_parquet("./data/data/train_data.parquet")
    test_data.to_parquet("./data/data/test_data.parquet")


def download_file():
    train_file = load_dataset("lvdthieu/sol_file", split="train")
    test_file = load_dataset("lvdthieu/sol_file", split="test")
    train_file = pd.DataFrame(train_file)
    test_file = pd.DataFrame(test_file)
    train_file.to_parquet("./data/solfile/train_file.parquet", engine="fastparquet")
    test_file.to_parquet("./data/solfile/test_file.parquet", engine="fastparquet")


def download_test():
    train = load_dataset("zhaospei/refine-v2", data_files="train.jsonl")
    test = load_dataset("zhaospei/refine-v2", data_files="test.jsonl")
    train = pd.DataFrame(train)
    test = pd.DataFrame(test)
    train.to_parquet("./data/test/train.parquet", engine="fastparquet")
    test.to_parquet("./data/test/test.parquet", engine="fastparquet")


def compilable(test_source):
    test = pd.read_parquet(test_source, engine="fastparquet").reset_index(drop=True)
    error_files = []
    pattern = r"contracts/(\w+\.sol)"

    for i in range(len(test)):
        source = test.loc[i, "source_code"]
        with open(f"./hardhat/contracts/sample_{i}.sol", "w") as f:
            f.write(source)
    wrong_file = [
        10417,
        10552,
        11668,
        11729,
        11884,
        1857,
        2106,
        3165,
        3352,
        4069,
        4259,
        4617,
        5572,
        5739,
        619,
        6485,
        6554,
        6566,
        6707,
        7646,
        8374,
        8457,
        8701,
        9136,
        9796,
        9818,
        10471,
    ]
    
    for file in wrong_file:
        error_files.append([file, "Wrong format of pragma soldity version"])
        run(
            f"""cd hardhat/contracts
            rm sample_{file}.sol""",
            shell=True,
        )

    cmd = """
        cd hardhat
        npx hardhat compile
        """
    cnt = 0
    while True:
        cnt += 1
        print("Loop:", cnt)
        data = run(cmd, shell=True, capture_output=True, text=True)
        output = data.stdout
        if output != "\n":
            break
        err = data.stderr
        print(
            err,
            "\n------------------------------------------------------------------------------\n",
        )
        err_comps = err.split("\n\n")
        print("Number of errors:", len(err_comps))
        loop_err_files = set()
        for err_comp in err_comps:
            for err_type in ERROR:
                if err_type in err_comp:
                    match = re.search(pattern, err_comp)
                    if match:
                        err_file = match.group(1)
                        print(f"{err_file}")
                        loop_err_files.add((err_file, err_comp))

        for err_file, err_comp in loop_err_files:
            idx = int(err_file.split(".")[0].split("_")[1])
            error_files.append([idx, err_comp])
            run(
                f"""cd hardhat/contracts
                rm {err_file}""",
                shell=True,
            )
            print("Remove:", err_file)
    error_files = pd.DataFrame(error_files, columns=["source_idx", "Error"])
    error_files.to_csv("error_files.csv")
    print(output)
    # print(repr(error))


if __name__ == "__main__":
    # download_file()
    # download_data()
    # download_test()
    
    compilable("./data/sol-file-v2/test_file.parquet")
