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
    train_data = load_dataset("andstor/smart_contracts", split="train")
    test_data = load_dataset("andstor/smart_contracts", split="test")
    valid_data = load_dataset("andstor/smart_contracts", split="validation")

    train_data = pd.DataFrame(train_data)
    # print(train_data.info())

    test_data = pd.DataFrame(test_data)
    # print(test_data.info())

    valid_data = pd.DataFrame(valid_data)
    # print(valid_data.info())

    train_data = train_data[["contract_name", "contract_address", "source_code"]]
    test_data = test_data[["contract_name", "contract_address", "source_code"]]
    valid_data = valid_data[["contract_name", "contract_address", "source_code"]]

    train_data = pd.concat([train_data, valid_data], axis=0).reset_index(drop=True)
    train_data = train_data.rename(
        columns={
            "contract_name": "file_name",
            "contract_address": "file_address",
            "source_code": "source_code",
        }
    )
    test_data = test_data.rename(
        columns={
            "contract_name": "file_name",
            "contract_address": "file_address",
            "source_code": "source_code",
        }
    )

    train_data.to_parquet("./data/solfile/train_data.parquet", engine="fastparquet")
    test_data.to_parquet("./data/solfile/test_data.parquet", engine="fastparquet")


if __name__ == "__main__":
    make_solidity_file_data()
    
