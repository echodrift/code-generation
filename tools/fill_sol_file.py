import pandas as pd
import argparse
import tqdm
from difflib import SequenceMatcher
import json


def get_location(source, element):
    start_line = element["loc"]["start"]["line"]
    start_col = element["loc"]["start"]["column"]
    end_line = element["loc"]["end"]["line"]
    end_col = element["loc"]["end"]["column"]
    lines = source.split('\n')
    start_idx = 0
    for i in range(start_line - 1):
        start_idx += len(lines[i])
    start_idx = start_idx + start_line - 1 + start_col
    
    end_idx = 0
    for i in range(end_line - 1):
        end_idx += len(lines[i])
    end_idx = end_idx + end_line - 1 + end_col + 1
    
    return start_idx, end_idx


sol_files = pd.read_parquet(
    "/home/hieuvd/lvdthieu/CodeGen/data/solfile/all_file_v2.parquet",
    engine="fastparquet",
)


def fill_contract(row):
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
            candidates = []
            for subNode in child["subNodes"]:
                if (
                    subNode["type"] == "FunctionDefinition"
                    and subNode["name"] == row["func_name"]
                ):
                    candidates.append(subNode)

            if len(candidates) == 0:
                return [None, None]
            elif len(candidates) == 1:
                body_start, body_end = get_location(source, candidates[0]["body"])
                filled_source_body = (
                    source[: body_start + 1] + row["func_body"] + source[body_end - 1 :]
                )
                filled_source_deepseek = (
                    source[: body_start + 1]
                    + row["deepseek_output"]
                    + source[body_end - 1 :]
                )
                return filled_source_body, filled_source_deepseek
            else:
                best_candidate = None
                best_similar_rate = 0
                for candidate in candidates:
                    body_start, body_end = get_location(source, candidate["body"])
                    ground_truth = source[body_start + 1 : body_end - 1]
                    similar_rate = SequenceMatcher(
                        None, ground_truth, row["func_body"]
                    ).ratio()
                    if best_similar_rate < similar_rate:
                        best_similar_rate = similar_rate
                        best_candidate = candidate

                body_start, body_end = get_location(source, best_candidate["body"])
                filled_source_body = (
                    source[: body_start + 1] + row["func_body"] + source[body_end - 1 :]
                )
                filled_source_deepseek = (
                    source[: body_start + 1]
                    + row["deepseek_output"]
                    + source[body_end - 1 :]
                )
                return filled_source_body, filled_source_deepseek


def make_test_suite(source, dest):
    df = pd.read_parquet(source, engine="fastparquet")
    df["filled_source_body"], df["filled_source_deepseek"] = zip(
        *df.apply(fill_contract, axis=1)
    )
    df.to_parquet(dest, engine="fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-o", "--output", dest="output")
    args = parser.parse_args()
    make_test_suite(args.input, args.output)
