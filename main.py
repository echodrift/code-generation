from func.dataset import read_ccgra_dataset, read_smartdoc_dataset
from func.sol_parse import capture_comments
import os
from setup import BASE_DIR


if __name__ == "__main__":
    print(capture_comments(os.path.join(BASE_DIR, "data", "sol", "sample.sol")))

    

