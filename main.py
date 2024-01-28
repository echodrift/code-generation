import pandas as pd

ERROR = [
    "ParserError",
    "DocstringParsingError",
    "SyntaxError",
    "DeclarationError",
    "TypeError",
    "UnimplementedFeatureError",
]


def make_raw_test_suite(file_path: str, output: str):
    """This function aims to create a more informative version for LLM output data

    Args:
        file_path (str): LLM output data file path
        output (str): File path to write new data version
    """
    test = pd.read_json(path_or_buf=file_path, lines=True)
    contracts = pd.read_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/contracts_filtered.parquet",
        engine="fastparquet",
    )
    test["file_source_idx"] = (
        test["source_idx"]
        .apply(lambda idx: contracts.loc[idx, "source_idx"])
        .astype("int64")
    )
    files = pd.read_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/solfile-v3/all_file.parquet",
        engine="fastparquet",
    )
    test["file_source"] = test["file_source_idx"].apply(
        lambda idx: files.loc[idx, "source_code"]
    )
    test.drop(
        columns=[
            "file_source_idx",
            "source_idx",
            "masked_contract",
        ],
        inplace=True,
    )
    test.to_parquet(output, engine="fastparquet")


def split_test_suite(file_path: str):
    test_suite = pd.read_parquet(file_path, engine="fastparquet")
    test_suite[
        [
            "contract_name",
            "func_name",
            "func_body",
            "func_body_removed_comment",
            "original_source_code",
        ]
    ].rename(columns={"original_source_code": "source_code"}).to_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/test/original.parquet", engine="fastparquet"
    )

    test_suite[
        [
            "contract_name",
            "func_name",
            "func_body",
            "func_body_removed_comment",
            "filled_source_body",
        ]
    ].rename(columns={"filled_source_body": "source_code"}).to_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/test/body.parquet", engine="fastparquet"
    )

    test_suite[
        [
            "contract_name",
            "func_name",
            "func_body",
            "func_body_removed_comment",
            "filled_source_deepseek",
        ]
    ].rename(columns={"filled_source_deepseek": "source_code"}).to_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/test/deepseek.parquet", engine="fastparquet"
    )


def write_sample():
    all_file = pd.read_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/solfile-v3/all_file.parquet",
        engine="fastparquet",
    )
    with open("sample.sol", "w") as f:
        f.write(all_file.sample(n=1, random_state=29).iloc[0, 0])


if __name__ == "__main__":
    # make_raw_test_suite(
    #     "/home/hieuvd/lvdthieu/CodeGen/data/train.jsonl",
    #     "/home/hieuvd/lvdthieu/CodeGen/data/raw_test_v1.parquet",
    # )
    split_test_suite("/home/hieuvd/lvdthieu/CodeGen/data/test_suite_v1.parquet")
