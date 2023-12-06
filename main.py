from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.sol_parse import get_pairs, capture_functions, capture_comments
import os
from setup import BASE_DIR
from datasets import load_dataset
import pandas as pd
from solidity_parser import parser

if __name__ == "__main__":
    # # dataset = load_dataset("andstor/smart_contracts")
    # # train_data = pd.DataFrame(dataset["train"])
    # # train_data.loc[:10, ["file_path", "source_code"]].to_csv("data.csv", index=False)
    
    # train_data = pd.read_csv("data.csv")
    # # with open("./data/sol/sample.sol", "r") as f:
    # # #     # f.write(train_data.loc[0, "source_code"])
    # #     sc = f.read()

    # # print(get_pairs(sc))
    
    # data = []
    # for i in range(len(train_data)):
    #     sc = train_data.loc[i, "source_code"].replace('\r\n', '\n')
    #     pairs = get_pairs(sc)
    #     if pairs:
    #         data.extend(get_pairs(sc))
    #     print("-----------------------------------")
        
    # result = pd.DataFrame(data, columns=["function", "specs"])
    # result.to_csv("test.csv")
    
    check = pd.read_csv("test.csv")
    print(check.loc[5, "specs"])
    print("-------------------------------")
    print(check.loc[5, "function"])


    
