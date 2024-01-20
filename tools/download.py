import pandas as pd
from datasets import load_dataset
import json
from datasets import disable_caching

disable_caching()


def download_data(dataset, split, type, store_dir, file_name=None):
    if file_name:
        data = load_dataset(dataset, data_files=file_name)
    else:
        data = load_dataset(dataset, split=split)
    if type == "parquet":
        data = pd.DataFrame(data)
    elif type == "jsonl":
        tmp = []
        for l in data["train"]:
            tmp.append(json.loads(l))
        data = pd.DataFrame(tmp)
    print(data.info())


download_data(
    "zhaospei/refine-v2",
    "test",
    "jsonl",
    "/home/hieuvd/lvdthieu/CodeGen/data/test",
    "test.jsonl",
)
