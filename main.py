import json
import os
from typing import List

import pandas as pd
from datasets import load_dataset
from solidity_parser import parser

from config import BASE_DIR
from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.params_generator import ParamGenerator
from func.sol_parse import SolidityParser


def make_solidity_file():
    train_data = load_dataset("andstor/smart_contracts", split="train")
    # print(train_data)
    test_data = load_dataset("andstor/smart_contracts", split="test")
    # print(test_data)
    valid_data = load_dataset("andstor/smart_contracts", split="validation")
    # print(valid_data)

    train_data = pd.DataFrame(train_data)
    # print(train_data.info())

    test_data = pd.DataFrame(test_data)
    # print(test_data.info())

    valid_data = pd.DataFrame(valid_data)
    # print(valid_data.info())

    train_data = train_data[["contract_address", "source_code"]]
    test_data = test_data[["contract_address", "source_code"]]
    valid_data = valid_data[["contract_address", "source_code"]]

    train_data = pd.concat([train_data, valid_data], axis=0).reset_index(drop=True)
    train_data = train_data.rename(
        columns={"file_path": "file_address", "source_code": "source_code"}
    )
    test_data = test_data.rename(
        columns={"file_path": "file_address", "source_code": "source_code"}
    )

    train_data.to_parquet("./data/solfile/train_data.parquet", engine="fastparquet")
    test_data.to_parquet("./data/solfile/test_data.parquet", engine="fastparquet")


if __name__ == "__main__":
    pass
