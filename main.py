import os

import pandas as pd
from datasets import load_dataset

from config import BASE_DIR
from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.params_generator import ParamGenerator
from func.sol_parse import get_pairs


def make_dataset():
    dataset = load_dataset("andstor/smart_contracts")
    train_data = pd.DataFrame(dataset["train"])
    valid_data = pd.DataFrame(dataset["validation"])
    test_data = pd.DataFrame(dataset["test"])
    data = pd.concat([train_data, valid_data, test_data], axis=0)

    all_pairs = []
    for i in range(len(data)):
        print(i)
        sc = data.loc[i, "source_code"].replace("\r\n", "\n")
        pairs = get_pairs(sc)
        if pairs:
            all_pairs.extend(get_pairs(sc))
        result = pd.DataFrame(all_pairs, columns=["function", "specs"])
        result.to_csv(os.path.join(BASE_DIR, "out", "pairs.csv"))


if __name__ == "__main__":
    with open(
        "/home/lvdthieu/Documents/Projects/CodeGen/hardhat/contracts/Lock.sol", "r"
    ) as f:
        contract = f.read()
    pg = ParamGenerator(contract)
    print(pg.generate_input("Lock", "withdraw"))
