import argparse
import json
import os
import random
import traceback
from collections import namedtuple
from typing import List, Optional, Tuple

import pandas as pd
from tqdm import tqdm


class ParsedObject:
    pass


SOL_FILES = pd.read_parquet(
    "/var/data/lvdthieu/code-generation/solidity_data/data/data/files.parquet",
    engine="fastparquet",
)
CONTRACTS = pd.read_parquet(
    "/var/data/lvdthieu/code-generation/solidity_data/data/data/contracts.parquet",
    engine="fastparquet"
)
ContractInfo = namedtuple("ContractInfo", "source_idx contract_name contract_source contract_ast count")
ASample = namedtuple("ASample", "source_idx contract_name func_name masked_body masked_all func_body signature_only signature_extend")
Location = namedtuple("Location", "start_line start_col end_line end_col")
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


def merging(input_dir: str, concurrency: int, output: str):
    """This function aims to merge multiple parquet files into one

    Args:
        input_dir (str): Directory path store parquet files
        concurrency (int): Number of parquet files
        output (str): File location to store result
    """
    dfs = []
    for i in range(1, concurrency + 1):
        dfs.append(
            pd.read_parquet(
                os.path.join(input_dir, f"result{i}.parquet"), engine="fastparquet"
            )
        )
    result = pd.concat(dfs, axis=0).reset_index(drop=True)
    result.to_parquet(output, engine="fastparquet")


def sharding(input: str, concurrency: int, output_dir: str):
    """This function aims to split large parquet file into multiple small parquet files

    Args:
        input (str): Large parquet file path
        concurrency (int): Number of small files want to split
        output_dir (str): Directory to store result
    """
    files_source = pd.read_parquet(input, engine="fastparquet").reset_index(drop=True)
    length = len(files_source)
    if length % concurrency == 0:
        chunk = length // concurrency
    else:
        chunk = length // concurrency + 1

    # files_source["source_idx"] = files_source.index

    for i in range(1, concurrency):
        files_source.iloc[(i - 1) * chunk : i * chunk].to_parquet(
            os.path.join(output_dir, f"batch{i}.parquet"),
            engine="fastparquet",
        )
    files_source.iloc[(concurrency - 1) * chunk :].to_parquet(
        os.path.join(output_dir, f"batch{concurrency}.parquet"),
        engine="fastparquet",
    )


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


def get_location(source: str, element: ParsedObject) -> Tuple[int, int]:
    """This function aims to get location of a specific element in Solidity source code

    Args:
        source (str): Solidity source code
        element (ParsedObject): an object in AST

    Returns:
        Tuple[int, int]: start index and end index of object
    """

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


def modified_get_location(solidity_code: str, loc: Location) -> Tuple[int, int]:
    lines = solidity_code.split('\n')
    start_idx = 0
    for i in range(loc.start_line - 1):
        start_idx += len(lines[i])
    start_idx = start_idx + loc.start_col + loc.start_line - 1

    end_idx = 0
    for i in range(loc.end_line - 1):
        end_idx += len(lines[i])
    end_idx = end_idx + loc.end_col + loc.end_line - 1
    return start_idx, end_idx


def fill_contract(row, sol_files: pd.DataFrame, column: str) -> str:
    """This function aims to create complete version of smart contract with output from LLMs 

    Args:
        row: Dataframe row which contains masked contract and LLMs output

    Returns:
        str: Filled contract
    """
    filled_contract = row["masked_contract"].replace(
        "<FILL_FUNCTION_BODY>", row[column] + '\n'
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
            filled_source= (
                source[:contract_start] + filled_contract + source[contract_end:]
            )
            return filled_source


def make_test_suite(source: str, dest: str, column: str):
    """Add fill_source columns to source dataset and save it to dest location

    Args:
        source (str): Source dataset location
        dest (str): Destination location to save processed result
    """
    df = pd.read_parquet(source, engine="fastparquet")
    df["source_code"] = df.apply(lambda row: fill_contract(row, sol_files=SOL_FILES, column=column), axis=1)
    df.to_parquet(dest, engine="fastparquet")


def make_raw_test_suite(input: str, output: str, sol_files: pd.DataFrame):
    """This function aims to create a more informative version for LLM output data

    Args:
        input (str): LLM output data file path
        output (str): File path to write new data version
    """
    test = pd.read_json(path_or_buf=input, lines=True)
    test["file_source_idx"] = (
        test["source_idx"]
        .apply(lambda idx: CONTRACTS.loc[idx, "source_idx"])
        .astype("int64")
    )
    test["file_source"] = test["file_source_idx"].apply(
        lambda idx: sol_files.loc[idx, "source_code"]
    )
    test.drop(
        columns=["source_idx"],
        inplace=True,
    )
    test.to_parquet(output, engine="fastparquet")


def get_inherit_element(input: str, output: str):
    """This function aims to add column contain inherit element info to input dataset and save to output location

    Args:
        input (str): input dataset location
        output (str): output location
    """

    df = pd.read_parquet(input, engine="fastparquet")
    # df.drop(columns=["source_idx"], inplace=True)
    
    all_file = pd.read_parquet(SOL_FILES_V2, engine="fastparquet")
    df["origin"], df["ast"]= zip(*df["file_source_idx"].apply(lambda idx: (all_file.loc[idx, "source_code"], all_file.loc[idx, "ast"])))


    def extract_inherit_element(source: str, ast: str, contract_name: str) -> str:
        """This function aims to get inherit element of a contract in specific source code

        Args:
            source (str): Smart contract source
            ast (str): AST of source
            contract_name (str): Contract name

        Returns:
            str: Inherit element list
        """
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
    
    def transform(row: pd.core.series.Series) -> str:
        return extract_inherit_element(row["origin"], row["ast"], row["contract_name"])

    df["inherit_elements"] = df.apply(transform, axis=1)
    df.drop(columns=["origin", "ast"], inplace=True)
    df.to_parquet(output, engine="fastparquet")


def get_compilable_rate(input: str):
    """Get compilable rate

    Args:
        input (str): Source dataset to calculate compilable rate
    """
    df = pd.read_parquet(input, engine="fastparquet")
    print("Compilable rate:", "{:.2%}".format(len(df[df["compile_info"] == "<COMPILED_SUCCESSFULLY>"]) / len(df)))


def get_in_out_variable(input: str, output: str):
    """This function aims to extract info about input and output variable of masked function

    Args:
        input (str): Source dataset location
        output (str): Output location
    """
    df = pd.read_parquet(input, engine="fastparquet")
    # df.drop(columns=["source_idx"], inplace=True)
    
    all_file = pd.read_parquet("/home/hieuvd/lvdthieu/CodeGen/data/solfile/all_file_v2.parquet", engine="fastparquet")
    df["origin"], df["ast"]= zip(*df["file_source_idx"].apply(lambda idx: (all_file.loc[idx, "source_code"], all_file.loc[idx, "ast"])))
    
    def extract_in_out_var(source: str, ast: str, contract_name: str, function_name: str) -> Tuple[str, str]:
        """This function aims to get inherit element of a contract in specific source code

        Args:
            source (str): Smart contract source
            ast (str): AST of source
            contract_name (str): Contract name

        Returns:
            str: Inherit element list
        """
        sourceUnit = json.loads(ast)
        source = source.replace("\r\n", '\n')
        func_lst = []
        for child in sourceUnit["children"]:
            if (child["type"] == "ContractDefinition" and
                child["kind"] == "contract" and 
                child["name"] == contract_name):
                for c in child["subNodes"]:
                    if c["type"] == "FunctionDefinition" and c["name"] == function_name:
                        func_lst.append(function_name)
        return func_lst

    def transform(row) -> str:
        return extract_in_out_var(row["origin"], row["ast"], row["contract_name"], row["func_name"])
    counter = {}
    for i in range(len(df)):
        num = len(transform(df.loc[i]))
        if num not in counter:
            counter[num] = 1
        else:
            counter[num] += 1
    
    print(counter)
    

def back_search(solidity_code: str, comment_list: List[dict], start_point: int, result: List[dict]):
    tmp = start_point
    while (solidity_code[tmp] == ' ' or solidity_code[tmp] == '\n' or solidity_code[tmp] == '\t' or solidity_code[tmp] == '\r'):
        tmp -= 1

    for comment in comment_list:
        if (tmp >= comment["range"]["start"] and tmp <= comment["range"]["end"]):
            result.append(comment["range"]["start"])
            back_search(solidity_code, comment_list, comment["range"]["start"] - 1, result)
            break


def mask_function(row) -> Optional[ASample]:
    try:
        contract_source = row["contract_source"].replace("\r\n", "\n")
        # Extract functions in a contract
        functions = []
        contract_ast = json.loads(row["contract_ast"])
        for subNode in contract_ast["children"][0]["subNodes"]:
            if subNode["type"] == "FunctionDefinition" and subNode["body"] and subNode["body"]["statements"]:
                func_loc = Location(subNode["loc"]["start"]["line"], subNode["loc"]["start"]["column"],
                                    subNode["loc"]["end"]["line"], subNode["loc"]["end"]["column"])
                func_body = subNode["body"]
                func_body_loc = Location(func_body["loc"]["start"]["line"], func_body["loc"]["start"]["column"],
                                         func_body["loc"]["end"]["line"], func_body["loc"]["end"]["column"])
                
                functions.append({"func_name": subNode["name"], 
                                  "func_loc": func_loc,
                                  "func_body_loc": func_body_loc})
        if not functions:
            return (None, None, None, None, None, None, None, None)
        
        # Randomly select a function
        def get_len(solidity_code: str, loc: Location) -> int:
            start_idx, end_idx = modified_get_location(solidity_code, loc)
            cnt = 0
            for i in range(start_idx, end_idx):
                if solidity_code[i] not in ['\n', '\t', '\r', '\a']:
                    cnt += 1
            return cnt
        for func in functions:
            func["func_body_len"] = get_len(contract_source, func["func_body_loc"])
        functions.sort(key=lambda func: func["func_body_len"])
        weights = [func["func_body_len"] for func in functions]
        for i in range(1, len(weights)):
            weights[i] = (weights[i - 1] + weights[i])
        total_weight = sum(weights)
        cumulative_weights = [weight / total_weight for weight in weights]
        random_function = random.choices(functions, weights=cumulative_weights, k=1)[0]

        # Mask function 

        # Mask function body
        func_body_start_idx, func_body_end_idx = modified_get_location(contract_source, random_function["func_body_loc"])
        masked_body = contract_source[0:func_body_start_idx + 1] + "<FILL_FUNCTION_BODY>" + \
                        contract_source[func_body_end_idx - 1:]
        func_body = contract_source[func_body_start_idx + 1 : func_body_end_idx - 1]

        # Mask function body and signature
        func_start_idx, func_end_idx = modified_get_location(contract_source, random_function["func_loc"])
        # Find comments
        comments = find_comment(contract_source)
        comment_start_idxes = [] 
        back_search(contract_source, comments, func_start_idx - 1, comment_start_idxes)
        start_idx = min(comment_start_idxes) if comment_start_idxes else func_start_idx
        masked_all = contract_source[0:start_idx] + "<FILL_FUNCTION>" + \
                    contract_source[func_end_idx + 1:]
        signature_only = contract_source[func_start_idx:func_body_start_idx]
        signature_extend = contract_source[start_idx:func_body_start_idx]
        return ASample(source_idx=row["source_idx"], 
                   contract_name=row["contract_name"],
                   func_name=random_function["func_name"],
                   masked_body=masked_body,
                   masked_all=masked_all,
                   func_body=func_body,
                   signature_only=signature_only,
                   signature_extend=signature_extend
                   ) 
    except:
        return (None, None, None, None, None, None, None, None)
    

def modified_mask_function(row) -> Optional[ASample]:
    try:
        contract_source = row["contract_source"].replace("\r\n", "\n")
        # Extract functions in a contract
        functions = []
        contract_ast = json.loads(row["contract_ast"])
        for subNode in contract_ast["children"][0]["subNodes"]:
            if subNode["type"] == "FunctionDefinition" and subNode["name"] == row["func_name"]:
                func_loc = Location(subNode["loc"]["start"]["line"], subNode["loc"]["start"]["column"],
                                    subNode["loc"]["end"]["line"], subNode["loc"]["end"]["column"])
                func_body = subNode["body"]
                func_body_loc = Location(func_body["loc"]["start"]["line"], func_body["loc"]["start"]["column"],
                                         func_body["loc"]["end"]["line"], func_body["loc"]["end"]["column"])
                functions.append({"func_name": subNode["name"], 
                                  "func_loc": func_loc,
                                  "func_body_loc": func_body_loc})
                
        # Mask function 
        if not functions:
            return (None, None, None, None, None, None, None, None)
        elif len(functions) == 1:
            random_function = functions[0] 
        else:
            start_idx = row["masked_contract"].find("<FILL_FUNCTION_BODY>")
            distances = []
            for function in functions:
                func_body_start_idx, func_body_end_idx = modified_get_location(contract_source, function["func_body_loc"])
                distances.append(abs(func_body_start_idx - start_idx))
            most_match = distances.index(min(distances))
            random_function = functions[most_match]
        # Mask function body
        func_body_start_idx, func_body_end_idx = modified_get_location(contract_source, random_function["func_body_loc"])
        masked_body = contract_source[0:func_body_start_idx + 1] + "<FILL_FUNCTION_BODY>" + \
                        contract_source[func_body_end_idx - 1:]
        func_body = contract_source[func_body_start_idx + 1 : func_body_end_idx - 1]

        # Mask function body and signature
        func_start_idx, func_end_idx = modified_get_location(contract_source, random_function["func_loc"])
        # Find comments
        comments = find_comment(contract_source)
        comment_start_idxes = [] 
        back_search(contract_source, comments, func_start_idx - 1, comment_start_idxes)
        start_idx = min(comment_start_idxes) if comment_start_idxes else func_start_idx
        masked_all = contract_source[0:start_idx] + "<FILL_FUNCTION>" + \
                    contract_source[func_end_idx + 1:]
        signature_only = contract_source[func_start_idx:func_body_start_idx]
        signature_extend = contract_source[start_idx:func_body_start_idx]
        return ASample(source_idx=row["source_idx"], 
                   contract_name=row["contract_name"],
                   func_name=random_function["func_name"],
                   masked_body=masked_body,
                   masked_all=masked_all,
                   func_body=func_body,
                   signature_only=signature_only,
                   signature_extend=signature_extend
                   ) 
    except Exception as e:
        with open("error.txt", "a") as f:
            f.write(f"{traceback.format_exc()}\n" + "-" * 200)
        return (None, None, None, None, None, None, None, None)


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
        case "raw_test":
            make_raw_test_suite(args.input, args.output, SOL_FILES)
        case "test_suite":
            make_test_suite(args.input, args.output, args.col)
        case "cr":
            get_compilable_rate(args.input)
        case "inherit_element":
            get_inherit_element(args.input, args.output)
        case "params_return_element":
            get_in_out_variable(args.input, args.output)
        case "make_dataset":
            tqdm.pandas()
            df = pd.read_parquet(args.input, "fastparquet")
            df = df.progress_apply(modified_mask_function, axis=1)
            df = pd.DataFrame(df.values.tolist(), columns=df.iloc[0]._fields)
            df.to_parquet(args.output, "fastparquet")
            