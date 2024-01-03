import os

import pandas as pd
from datasets import load_dataset
from solidity_parser import parser

from config import BASE_DIR
from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.params_generator import ParamGenerator
from func.sol_parse import get_pairs
import json


def make_dataset():
    dataset = load_dataset("andstor/smart_contracts")

    train_data = pd.DataFrame(dataset["train"])
    valid_data = pd.DataFrame(dataset["validation"])
    test_data = pd.DataFrame(dataset["test"])
    data = pd.concat([train_data, valid_data, test_data], axis=0)
    test_data.to_csv(os.path.join(BASE_DIR, "out", "test_data.csv"), index=True)
    # all_pairs = []
    # for i in range(len(data)):
    #     print(i)
    #     sc = data.loc[i, "source_code"].replace("\r\n", "\n")
    #     pairs = get_pairs(sc)
    #     if pairs:
    #         all_pairs.extend(get_pairs(sc))
    #     result = pd.DataFrame(all_pairs, columns=["function", "specs"])
    #     result.to_csv(os.path.join(BASE_DIR, "out", "pairs.csv"))


def test_parser(contract):
    sourceUnit = parser.parse(contract, loc=True)
    return sourceUnit


if __name__ == "__main__":
    # with open(
    #     "/home/lvdthieu/Documents/Projects/CodeGen/hardhat/contracts/Lock.sol", "r"
    # ) as f:
    #     contract = f.read()
    # pg = ParamGenerator(contract)
    # print(pg.generate_input("Lock", "withdraw"))

    # test_data = pd.read_csv(os.path.join(BASE_DIR, "out", "test_data.csv"))
    # output_file = os.path.join(BASE_DIR, "out", "output2.sol")
    # with open(output_file, "w") as f:
    #     f.write(test_data.loc[1, "source_code"])

    with open(
        "/home/lvdthieu/Documents/Projects/CodeGen/data/sol/DummyTel.sol", "r"
    ) as f:
        contract = f.read()
    with open("test.json", "w") as f:
        f.write(json.dumps(test_parser(contract)))
