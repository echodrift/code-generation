import pandas as pd
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def read_ccgra_dataset():
    ccgra_train_ast = pd.read_json(
        path_or_buf=os.path.join(BASE, "data", "ccgra", "train_ast.jsonl"),
        lines=True,
    )
    ccgra_train = pd.read_json(
        path_or_buf=os.path.join(BASE, "data", "ccgra", "train_base.jsonl"),
        lines=True,
    )
    ccgra_train["ast"] = ccgra_train_ast["ast"]

    ccgra_test_ast = pd.read_json(
        path_or_buf=os.path.join(BASE, "data", "ccgra", "test_ast.jsonl"),
        lines=True,
    )
    ccgra_test = pd.read_json(
        path_or_buf=os.path.join(BASE, "data", "ccgra", "test_base.jsonl"),
        lines=True,
    )
    ccgra_test["ast"] = ccgra_test_ast["ast"]

    ccgra_valid_ast = pd.read_json(
        path_or_buf=os.path.join(BASE, "data", "ccgra", "valid_ast.jsonl"),
        lines=True,
    )
    ccgra_valid = pd.read_json(
        path_or_buf=os.path.join(BASE, "data", "ccgra", "valid_base.jsonl"),
        lines=True,
    )
    ccgra_valid["ast"] = ccgra_valid_ast["ast"]

    ccgra = pd.concat([ccgra_train, ccgra_test, ccgra_valid], axis=0)
    ccgra.to_csv(path_or_buf=os.path.join(BASE, "out", "ccgra.csv"), index=False)


def read_smartdoc_dataset():
    with open(
        os.path.join(BASE, "data", "smartdoc", "train/train.token.code"), "r"
    ) as f:
        smartdoc_train_code = f.readlines()
    with open(
        os.path.join(BASE, "data", "smartdoc", "train/train.token.nl"), "r"
    ) as f:
        smartdoc_train_nl = f.readlines()
    smartdoc_train = pd.DataFrame(
        {"code": smartdoc_train_code, "nl": smartdoc_train_nl}
    )
    with open(
        os.path.join(BASE, "data", "smartdoc", "test/test.token.code"), "r"
    ) as f:
        smartdoc_test_code = f.readlines()
    with open(
        os.path.join(BASE, "data", "smartdoc", "test/test.token.nl"), "r"
    ) as f:
        smartdoc_test_nl = f.readlines()
    smartdoc_test = pd.DataFrame({"code": smartdoc_test_code, "nl": smartdoc_test_nl})

    smartdoc = pd.concat([smartdoc_train, smartdoc_test], axis=0)
    smartdoc.to_csv(
        path_or_buf=os.path.join(BASE, "out", "smartdoc.csv"), index=False
    )
