from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.sol_parse import capture_comments, capture_functions
import os
from setup import BASE_DIR
from datasets import load_dataset
from solidity_parser import parser

if __name__ == "__main__":
    # dataset = load_dataset("andstor/smart_contracts")
    # train_data = dataset["train"]
    # print(train_data["source_code"][0])
    with open("./data/sol/counter.sol", 'r') as f:
        sc = f.read()
    
    capture_functions(sc)
    
