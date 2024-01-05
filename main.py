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


if __name__ == "__main__":
    # contracts = pd.read_csv("./out/contracts.csv")
    #print(contracts.info())
    test_sol_file = pd.read_csv("./data/solfile/test_sol_file.csv")
    with open("error.sol", "w") as f:
        f.write(test_sol_file.loc[201, "source_code"])
