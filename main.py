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


if __name__ == "__main__":
    train_data = load_dataset("zhaospei/smart-contract-gen", split="train")
    print(train_data)
    test_data = load_dataset("zhaospei/smart-contract-gen", split="test")
    print(test_data)
    
    train_data = pd.DataFrame(train_data)
    print(train_data.info())
    
    test_data = pd.DataFrame(test_data)
    print(test_data.info())
    
    train_data.to_parquet("./data/data/train_data.parquet", engine="fastparquet")
    test_data.to_parquet("./data/data/test_data.parquet", engine="fastparquet")