import json
import os
from typing import List

import pandas as pd
from datasets import load_dataset

from config import BASE_DIR
from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.params_generator import ParamGenerator
from func.sol_parse import SolidityParser


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
            "abi",
            "compiler_version",
            "library",
            "language",
        ]
    ]
    test_file = test_file[
        [
            "contract_name",
            "contract_address",
            "source_code",
            "abi",
            "compiler_version",
            "library",
            "language",
        ]
    ]
    valid_file = valid_file[
        [
            "contract_name",
            "contract_address",
            "source_code",
            "abi",
            "compiler_version",
            "library",
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
    

if __name__ == "__main__":
    make_solidity_file_data()
