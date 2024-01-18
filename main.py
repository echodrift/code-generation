import json
import os
from typing import List

import pandas as pd
from datasets import load_dataset
from subprocess import run


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
    print(train)
    print(test)
    # train = pd.read_json(train, lines=True)
    # test = pd.read_json(test, lines=True)
    # print(train.info())
    # print(test.info())
    # train.to_parquet("./data/test/train.parquet", engine="fastparquet")
    # test.to_parquet("./data/test/test.parquet", engine="fastparquet")


def compilable(test_source):
    test = pd.read_parquet(test_source, engine="fastparquet").reset_index(drop=True)
    for i in range(len(test)):
        source = test.loc[i, "source_code_with_deepseek_output"]
        with open(f"./hardhat/contracts/sample_{i}.sol", "w") as f:
            f.write(source)

    cmd = """
    cd hardhat
    npx hardhat compile
    """
    data = run(cmd, capture_output=True, shell=True, text=True)
    output = data.stdout
    error = data.stderr
    with open("output.txt", "w") as f:
        f.write(output)
    with open("error.txt", "w") as f:
        f.write(error)


if __name__ == "__main__":
    # download_file()
    # download_data()
    # download_test()
    compilable("./data/test/test-v3.parquet")
