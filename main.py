import os

import pandas as pd
from datasets import load_dataset
from solidity_parser import parser

from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.params_generator import ParamGenerator
from func.sol_parse import get_pairs
from setup import BASE_DIR

if __name__ == "__main__":
    # dataset = load_dataset("andstor/smart_contracts")
    # train_data = pd.DataFrame(dataset["train"])
    # valid_data = pd.DataFrame(dataset["validation"])
    # test_data = pd.DataFrame(dataset["test"])
    # data = pd.concat([train_data, valid_data, test_data], axis=0)

    # all_pairs = []
    # for i in range(19131, len(data)):
    #     print(i)
    #     sc = data.loc[i, "source_code"].replace('\r\n', '\n')
    #     pairs = get_pairs(sc)
    #     if pairs:
    #         all_pairs.extend(get_pairs(sc))
    #     result = pd.DataFrame(all_pairs, columns=["function", "specs"])
    #     result.to_csv(os.path.join(BASE_DIR, "out", "pairs.csv"))
    with open(
        "/home/lvdthieu/Documents/Projects/CodeGen/data/sol/DummyTel.sol", "r"
    ) as f:
        contract = f.read()
    pg = ParamGenerator(contract)
    pg.generate_input("DummyTel", "test")
