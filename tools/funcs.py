import os
import argparse
import pandas as pd
from typing import Optional, List
from difflib import SequenceMatcher
import json


sol_files = pd.read_parquet(
    "/home/hieuvd/lvdthieu/CodeGen/data/solfile/all_file_v2.parquet",
    engine="fastparquet",
)

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


def merging(files_source: str, concurrency: int, output: str):
    """This function aims to merge multiple parquet files into one

    Args:
        files_source (str): Directory path store parquet files
        concurrency (int): Number of parquet files
        output (str): File location to store result
    """
    dfs = []
    for i in range(1, concurrency + 1):
        dfs.append(
            pd.read_parquet(
                os.path.join(files_source, f"result{i}.parquet"), engine="fastparquet"
            )
        )
    result = pd.concat(dfs, axis=0).reset_index(drop=True)
    result.to_parquet(output, engine="fastparquet")


def sharding(input: str, concurrency: int, output: str):
    """This function aims to split large parquet file into multiple small parquet files

    Args:
        input (str): Large parquet file path
        concurrency (int): Number of small files want to split
        output (str): Directory to store result
    """
    files_source = pd.read_parquet(input, engine="fastparquet").reset_index(drop=True)
    length = len(files_source)
    if length % concurrency == 0:
        chunk = length // concurrency
    else:
        chunk = length // concurrency + 1

    files_source["source_idx"] = files_source.index

    for i in range(1, concurrency):
        files_source.iloc[(i - 1) * chunk : i * chunk].to_parquet(
            os.path.join(output, f"batch{i}.parquet"),
            engine="fastparquet",
        )
    files_source.iloc[(concurrency - 1) * chunk :].to_parquet(
        os.path.join(output, f"batch{concurrency}.parquet"),
        engine="fastparquet",
    )


############################################################################################################
"""These functions aims for removing comment in solidity source code
"""


def find_comment(source: str) -> Optional[List[dict]]:
    """This function aims to find all comments in Solidity source code

    Args:
        source (str): Solidity source code

    Returns:
        List[dict]: List of dictionary contains comment's information
    """
    source = source.replace("\r\n", "\n")
    state = "ETC"
    i = 0
    comments = []
    currentComment = None

    while i + 1 < len(source):
        if state == "ETC" and source[i] == "/" and source[i + 1] == "/":
            state = "LINE_COMMENT"
            currentComment = {"type": "LineComment", "range": {"start": i}}
            i += 2
            continue

        if state == "LINE_COMMENT" and source[i] == "\n":
            state = "ETC"
            currentComment["range"]["end"] = i
            comments.append(currentComment)
            currentComment = None
            i += 1
            continue

        if state == "ETC" and source[i] == "/" and source[i + 1] == "*":
            state = "BLOCK_COMMENT"
            currentComment = {"type": "BlockComment", "range": {"start": i}}
            i += 2
            continue

        if state == "BLOCK_COMMENT" and source[i] == "*" and source[i + 1] == "/":
            state = "ETC"
            currentComment["range"]["end"] = i + 2
            comments.append(currentComment)
            currentComment = None
            i += 2
            continue
        i += 1

    if currentComment and currentComment["type"] == "LineComment":
        if source[i - 1] == "\n":
            currentComment["range"]["end"] = len(source) - 1
        else:
            currentComment["range"]["end"] = len(source)

        comments.append(currentComment)

    return comments


def remove_comment(source: str) -> str:
    """This function aims to remove all comments in Solidity source code

    Args:
        source (str): Original Solidity source code

    Returns:
        str: Source code after remove comments
    """
    source = source.replace("\r\n", "\n")
    comments = find_comment(source)
    removed_comment = ""
    begin = 0
    for comment in comments:
        removed_comment += source[begin : comment["range"]["start"]]
        begin = comment["range"]["end"]
    removed_comment += source[begin:]
    return removed_comment


############################################################################################################
"""These functions aim for filling contract 
"""


def get_location(source, element):
    start_line = element["loc"]["start"]["line"]
    start_col = element["loc"]["start"]["column"]
    end_line = element["loc"]["end"]["line"]
    end_col = element["loc"]["end"]["column"]
    lines = source.split("\n")
    start_idx = 0
    for i in range(start_line - 1):
        start_idx += len(lines[i])
    start_idx = start_idx + start_line - 1 + start_col

    end_idx = 0
    for i in range(end_line - 1):
        end_idx += len(lines[i])
    end_idx = end_idx + end_line - 1 + end_col + 1

    return start_idx, end_idx


def fill_contract(row):
    contract_deepseek = row["masked_contract"].replace(
        "<FILL_FUNCTION_BODY>", row["deepseek_output"] + '\n'
    )
    contract_body = row["masked_contract"].replace(
        "<FILL_FUNCTION_BODY>", row["func_body"] + '\n'
    )
    source = row["file_source"].replace("\r\n", "\n")
    sourceUnit = json.loads(sol_files.loc[row["file_source_idx"], "ast"])
    if sourceUnit == "<PARSER_ERROR>":
        return [None, None]
    for child in sourceUnit["children"]:
        if (
            child["type"] == "ContractDefinition"
            and child["kind"] == "contract"
            and child["name"] == row["contract_name"]
        ):
            contract_start, contract_end = get_location(source, child)
            filled_source_body = (
                source[:contract_start] + contract_body + source[contract_end:]
            )
            filled_source_deepseek = (
                source[:contract_start] + contract_deepseek + source[contract_end:]
            )
            return filled_source_body, filled_source_deepseek


def make_test_suite(source, dest):
    df = pd.read_parquet(source, engine="fastparquet")
    df["filled_source_body"], df["filled_source_deepseek"] = zip(
        *df.apply(fill_contract, axis=1)
    )
    df.to_parquet(dest, engine="fastparquet")


############################################################################################################


def make_raw_test_suite(file_path: str, output: str):
    """This function aims to create a more informative version for LLM output data

    Args:
        file_path (str): LLM output data file path
        output (str): File path to write new data version
    """
    test = pd.read_json(path_or_buf=file_path, lines=True)
    contracts = pd.read_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/contracts/contracts_filtered.parquet",
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


def split_test_suite(file_path: str, output_dir: str):
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
        f"{output_dir}/body.parquet", engine="fastparquet"
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
        f"{output_dir}/deepseek.parquet", engine="fastparquet"
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


def get_inherit_element(file_path: str, output: str):
    df = pd.read_parquet(file_path, engine="fastparquet")
    df.drop(columns=["source_idx"], inplace=True)
    
    all_file = pd.read_parquet("/home/hieuvd/lvdthieu/CodeGen/data/solfile/all_file_v2.parquet", engine="fastparquet")
    df["origin"], df["ast"]= zip(*df["file_source_idx"].apply(lambda idx: (all_file.loc[idx, "source_code"], all_file.loc[idx, "ast"])))


    def extract_inherit_element(source: str, ast: str, contract_name: str):
        sourceUnit = json.loads(ast)
        source = source.replace("\r\n", '\n')
        inherit_elements = []
        for child in sourceUnit["children"]:
            if (child["type"] == "ContractDefinition" and
                child["kind"] == "contract" and 
                child["name"] == contract_name):
                base_contracts = [base_contract["baseName"]["namePath"] for base_contract in child["baseContracts"]]
                while base_contracts:
                    base_contract = base_contracts.pop(0)
                    
                    for child1 in sourceUnit["children"]:
                        if (child1["type"] == "ContractDefinition" and
                            child1["name"] == base_contract):
                            # Add base contract of base contract if there is 
                            ancestors = [base_contract["baseName"]["namePath"] for base_contract in child1["baseContracts"]]
                            base_contracts.extend(ancestors)
                            
                            for subNode in child1["subNodes"]:
                                # Add inherit variable 
                                if (subNode["type"] == "StateVariableDeclaration" and 
                                    subNode["variables"][0]["visibility"] != "private"):
                                        start_el, end_el = get_location(source, subNode)
                                        inherit_elements.append(source[start_el:end_el])
                                # Add inherit function
                                if (subNode["type"] == "FunctionDefinition" and
                                    subNode["visibility"] != "external" and
                                    subNode["visibility"] != "private"):
                                    start_func, end_func = get_location(source, subNode)
                                    if subNode["body"]:
                                        start_body, end_body = get_location(source, subNode["body"])
                                        inherit_elements.append(source[start_func:start_body] + "{<BODY>}")
                                    else:
                                        inherit_elements.append(source[start_func:end_func])
                            break
                break
        return str(inherit_elements)
    
    def transform(row):
        return extract_inherit_element(row["origin"], row["ast"], row["contract_name"])

    df["inherit_elements"] = df.apply(transform, axis=1)
    df.drop(columns=["origin", "ast"], inplace=True)
    df.to_parquet(output, engine="fastparquet")


def get_compilable_rate(file_path: str):
    df = pd.read_parquet(file_path, engine="fastparquet")
    print("Compilable rate:", "{:.2%}".format(len(df[df["compile_info"] == "<COMPILED_SUCCESSFULLY>"]) / len(df)))
                    
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--func", dest="func")
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-c", "--concurrency", dest="concurrency")
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("--col", dest="col")
    args = parser.parse_args()

    match args.func:
        case "sharding":
            sharding(args.input, int(args.concurrency), args.output)
        case "merging":
            merging(args.input, int(args.concurrency), args.output)
        case "remove_comment":
            df = pd.read_parquet(args.input, engine="fastparquet")
            df[f"{args.col}_removed_comment"] = df[args.col].apply(
                lambda source: remove_comment(source)
            )
            df.to_parquet(args.output, engine="fastparquet")
        case "test_suite":
            make_test_suite(args.input, args.output)
        case "raw_test":
            make_raw_test_suite(args.input, args.output)
        case "split_test_suite":
            split_test_suite(args.input, args.output)
        case "extract_error":
            extract_error(args.input, args.output)
        case "cr":
            get_compilable_rate(args.input)
        case "inherit_element":
            get_inherit_element(args.input, args.output)