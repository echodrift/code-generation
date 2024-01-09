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


def load_sol_file():
    dataset = load_dataset("andstor/smart_contracts")
    train_sol_file = pd.DataFrame(dataset["train"])[["contract_address", "source_code"]]
    valid_sol_file = pd.DataFrame(dataset["validation"])[["contract_address", "source_code"]]
    test_sol_file = pd.DataFrame(dataset["test"])[["contract_address", "source_code"]]
    return train_sol_file, valid_sol_file, test_sol_file


def extract_contracts(sol_file: str):
    sol_file = sol_file.replace("\r\n", "\n")
    contracts = []
    sourceUnit = parser.parse(sol_file, loc=True)
    lines = sol_file.splitlines()
    for child in sourceUnit["children"]:
        if child["type"] == "ContractDefinition":
            if child["kind"] in ["interface", "library", "abstract"]:
                return False
            else:
                if child["baseContracts"]:
                    break
                else:
                    start_line = child["loc"]["start"]["line"]
                    start_col = child["loc"]["start"]["column"]
                    end_line = child["loc"]["end"]["line"]
                    end_col = child["loc"]["end"]["column"]
                    start_idx = (
                        sum([len(lines[i]) for i in range(start_line - 1)])
                        + start_line
                        - 1
                        + start_col
                    )
                    end_idx = (
                        sum([len(lines[i]) for i in range(end_line - 1)])
                        + end_line
                        - 1
                        + end_col
                        + 1
                    )
                    contracts.append(sol_file[start_idx:end_idx])
    return contracts


def make_dataset(sol_files):
    contracts = []
    for i in range(len(sol_files)):
        print(i)
        try:
            tmp = extract_contracts(sol_files.loc[i, "source_code"])
            if tmp:
                contracts.extend(tmp)
        except:
            with open("error_log.txt", "a") as f:
                f.write(str(i) + "\n")
    
    print(len(contracts))


def mask_function(contracts):
    pass


def fix_data():
    data = pd.read_parquet("./out/all_data_train.parquet", engine="fastparquet")
    data = data.rename(columns={"contract_index": "function_name", "function_name": "contract_masked", 
                              "contract_masked": "function_body", "function_body": "function_requirement",
                              "function_requirement": "delete"})
    data = data.drop(columns=["delete"], axis=1)

    data.to_parquet("./out/all_data_train.parquet", engine="fastparquet")


if __name__ == "__main__":
    data = []
    for i in range(19):
        try:
            data.append(pd.read_csv(f"./out/data{i}.csv"))
        except:
            print(i)
    all_data = pd.concat(data, axis=0).reset_index()
    all_data.to_parquet("all_data_valid.parquet", engine="fastparquet")

    data = pd.read_parquet("./out/all_data_valid.parquet", engine="fastparquet")
    print(data.info())

    # data = pd.read_csv("./data/solfile/valid_sol_file.csv")
    
    # print(data[data["contract_address"] == "0x37fcf9870ea0a5b2dea3f84b8b041ab49d7410b4"])
    # with open("demo.sol", "w") as f:
    #     f.write(data[data["contract_address"] == "0x37fcf9870ea0a5b2dea3f84b8b041ab49d7410b4"].loc[876, "source_code"])