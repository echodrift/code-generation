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

    for i in range(100):
        source = test.loc[i, "source_code"]
        with open(f"./hardhat/contracts/sample_{i}.sol", "w") as f:
            f.write(source)
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
        error = data.stderr
        errors = error.split("\n\n")
        print("Number of errors:", len(errors))
        with open("error.txt", "a") as f:
            for err in errors:
                for err_type in ERROR:
                    if err_type in err:
                        f.write(
                            f"{err}\n___________________________________________________________________________\n"
                        )
                        match = re.search(pattern, err)
                        if match:
                            file_name = match.group(1)
                            print(f"{file_name}")
                            idx = int(file_name.split(".")[0].split("_")[1])
                            error_files.append([idx, err])
                            run(
                                f"""cd hardhat/contracts
                                rm {file_name}""",
                                shell=True,
                            )
                            print("Remove:", file_name)
    error_files = pd.DataFrame(error_files, columns=["source_idx", "Error"])
    error_files.to_csv("error_files.csv")
    # print(repr(error))


if __name__ == "__main__":
    # download_file()
    # download_data()
    # download_test()
    compilable("./data/sol-file-v2/test_file.parquet")
