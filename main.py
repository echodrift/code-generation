import pandas as pd

ERROR = [
    "ParserError",
    "DocstringParsingError",
    "SyntaxError",
    "DeclarationError",
    "TypeError",
    "UnimplementedFeatureError",
    "InternalCompilerError",
    "Exception",
    "CompilerError",
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
        "/home/hieuvd/lvdthieu/CodeGen/data/solfile/all_file.parquet",
        engine="fastparquet",
    )
    test["file_source"] = test["file_source_idx"].apply(
        lambda idx: files.loc[idx, "source_code"]
    )
    test.drop(
        columns=["source_idx"],
        inplace=True,
    )
    test.to_parquet(output, engine="fastparquet")


def split_test_suite(file_path: str):
    test_suite = pd.read_parquet(file_path, engine="fastparquet")
    test_suite[
        [
            "contract_name",
            "func_name",
            "masked_contract",
            "func_body",
            "func_body_removed_comment",
            "file_source_idx",
            "filled_source_body",
        ]
    ].rename(columns={"filled_source_body": "source_code"}).to_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/test/body.parquet", engine="fastparquet"
    )

    test_suite[
        [
            "contract_name",
            "func_name",
            "masked_contract",
            "func_body",
            "func_body_removed_comment",
            "deepseek_output",
            "file_source_idx",
            "filled_source_deepseek",
        ]
    ].rename(columns={"filled_source_deepseek": "source_code"}).to_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/test/deepseek.parquet", engine="fastparquet"
    )


def extract_error(file_path: str, output: str):
    """This function aims to extract error message from compiler output

    Args:
        file_path (str): Compiler output data file path
        output (str): Result data file path
    """
    source = pd.read_parquet(file_path, engine="fastparquet")

    def transform(string: str) -> str:
        if string == "<COMPILED_SUCCESSFULLY>":
            return string
        else:
            errors = []
            comps = string.split("\n\n")
            for comp in comps:
                for err in ERROR:
                    if err in comp:
                        errors.append(comp)
            return "\n".join(errors)

    source["compile_info"] = source["compile_info"].apply(lambda x: transform(x))

    source.to_parquet(output, engine="fastparquet")


if __name__ == "__main__":
    # make_raw_test_suite(
    #     "/home/hieuvd/lvdthieu/CodeGen/data/train.jsonl",
    #     "/home/hieuvd/lvdthieu/CodeGen/data/raw_test_v1.parquet",
    # )
    # split_test_suite("/home/hieuvd/lvdthieu/CodeGen/data/test_suite_v1.parquet")
    extract_error(
        "/home/hieuvd/lvdthieu/CodeGen/data/compile_info/deepseek.parquet",
        "/home/hieuvd/lvdthieu/CodeGen/data/compile_info/deepseek_v1.parquet",
    )
