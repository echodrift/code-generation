import argparse
import codecs
import random
import re
from typing import List, Optional, Tuple

import pandas as pd
from antlr4 import *
from java.java8.JavaLexer import JavaLexer
from java.java8.JavaParser import JavaParser
from java.java8.JavaParserListener import JavaParserListener
from tqdm import tqdm
from subprocess import run
import multiprocessing as mp
from itertools import repeat
from dataclasses import dataclass

@dataclass
class ASample:
    class_name: str
    func_name: str
    masked_class: str
    func_body: str


@dataclass
class Location:
    start_line: int
    start_col: int
    end_line: int
    end_col: int


@dataclass
class Function:
    class_name: str
    class_loc: Location
    func_name: str
    func_body_loc: Location


class ExtractFunc(JavaParserListener):
    def __init__(self):
        super().__init__()
        self.functions = []

    def enterClassDeclaration(self, ctx):
        self.class_name = ctx.identifier().getText()
        self.class_loc = Location(
            ctx.start.line,
            ctx.start.column,
            ctx.stop.line,
            ctx.stop.column + len(ctx.stop.text),
        )

    def enterMethodDeclaration(self, ctx):
        # If method is void method ignore it
        # if ctx.typeTypeOrVoid().getText() == "void":
        #     return
        self.func_name = ctx.identifier().getText()
        body = ctx.methodBody().block()
        if not body:
            return
        self.func_body_loc = Location(
            body.start.line,
            body.start.column,
            body.stop.line,
            body.stop.column + len(body.stop.text),
        )
        try:
            self.functions.append(
                {
                    "class_name": self.class_name,
                    "class_loc": self.class_loc,
                    "func_name": self.func_name,
                    "func_body_loc": self.func_body_loc,
                }
            )
        except:
            pass

    def get_functions(self):
        return self.functions


def get_location(java_code: str, loc: Location) -> Tuple[int, int]:
    lines = java_code.split("\n")
    start_idx = 0
    for i in range(loc.start_line - 1):
        start_idx += len(lines[i])
    start_idx = start_idx + loc.start_col + loc.start_line - 1

    end_idx = 0
    for i in range(loc.end_line - 1):
        end_idx += len(lines[i])
    end_idx = end_idx + loc.end_col + loc.end_line - 1
    return start_idx, end_idx


def get_functions(java_code: str) -> Optional[List[Function]]:
    try:
        input_stream = InputStream(java_code)
        lexer = JavaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = JavaParser(token_stream)
        tree = parser.compilationUnit()
        # Create listener
        listener = ExtractFunc()
        # Walk the parse tree
        walker = ParseTreeWalker()
        walker.walk(listener, tree)
        functions = listener.get_functions()
    except:
        return None
    return functions


def mask_function(java_code: str) -> Optional[ASample]:
    functions = get_functions(java_code)
    if not functions:
        return None
    # Randomly select a function
    random_function = random.choice(functions)

    # Extract function body
    class_start_idx, class_end_idx = get_location(
        java_code, random_function["class_loc"]
    )
    func_body_start_idx, func_body_end_idx = get_location(
        java_code, random_function["func_body_loc"]
    )
    masked_class = (
        java_code[class_start_idx : func_body_start_idx + 1]
        + "<FILL_FUNCTION_BODY>"
        + java_code[func_body_end_idx - 1 : class_end_idx]
    )
    func_body = java_code[func_body_start_idx + 1 : func_body_end_idx - 1]

    return ASample(
        class_name=random_function["class_name"],
        func_name=random_function["func_name"],
        masked_class=masked_class,
        func_body=func_body,
    )


def modified_mask_function(java_code: str) -> Optional[ASample]:
    functions = get_functions(java_code)
    if not functions:
        return None

    # Weighted random a function based on function body length
    # the more function long, the more probability it would be chose
    def get_len(java_code: str, loc: Location) -> int:
        start_idx, end_idx = get_location(java_code, loc)
        return end_idx - start_idx

    functions_with_len_body = [
        [get_len(java_code, func["func_body_loc"]), func] for func in functions
    ]
    functions_with_len_body.sort(key=lambda x: x[0])
    weights, functions = zip(*functions_with_len_body)
    weights = list(weights)
    functions = list(functions)
    for i in range(1, len(weights)):
        weights[i] = weights[i - 1] + weights[i]

    total = sum(weights)
    cumulative_weights = [weight / total for weight in weights]
    random_function = random.choices(functions, weights=cumulative_weights, k=1)[0]

    # Extract function body
    class_start_idx, class_end_idx = get_location(
        java_code, random_function["class_loc"]
    )
    func_body_start_idx, func_body_end_idx = get_location(
        java_code, random_function["func_body_loc"]
    )
    masked_class = (
        java_code[class_start_idx : func_body_start_idx + 1]
        + "<FILL_FUNCTION_BODY>"
        + java_code[func_body_end_idx - 1 : class_end_idx]
    )
    func_body = java_code[func_body_start_idx + 1 : func_body_end_idx - 1]

    return ASample(
        class_name=random_function["class_name"],
        func_name=random_function["func_name"],
        masked_class=masked_class,
        func_body=func_body,
    )


def make_a_sample(argument: Tuple[str, str, str]):
    java_file_url, project_name, relative_path = argument
    with codecs.open(java_file_url, "r", encoding="utf-8", errors="ignore") as f:
        try:
            java_code = f.read()
            # sample = mask_function(java_code)
            sample = modified_mask_function(java_code)
            if sample:
                return {"proj_name": project_name,
                        "relative_path": relative_path,
                        "class_name": sample.class_name,
                        "func_name": sample.func_name,
                        "masked_class": sample.masked_class,
                        "func_body": sample.func_body}
            else:
                return {"proj_name": project_name,
                        "relative_path": relative_path,
                        "class_name": None,
                        "func_name": None,
                        "masked_class": None,
                        "func_body": None}
        except:
            return {"proj_name": None,
                    "relative_path": None,
                    "class_name": None,
                    "func_name": None,
                    "masked_class": None,
                    "func_body": None}
    

def make_dataset(
    java_files: pd.DataFrame,
    repos_directory: str,
    num_process: int = 10
) -> pd.DataFrame:
    """Make dataset

    Args:
        java_file_urls (str): java file urls
        repos_directory (str): path to diretory of repositories
        num_process (int): number of concurrent processes. Default: 10.

    Returns:
        pd.DataFrame: Dataset
    """
    iteration = len(java_files)
    tqdm.pandas(desc="Making absolute url")
    java_files["absolute_url"] = java_files["java_files"].progress_apply(lambda file: f"{repos_directory}/{file}")

    arguments = list(zip(java_files["absolute_url"], java_files["proj_name"], java_files["relative_path"]))
    with mp.Pool(processes=num_process) as pool:
        rows = list(tqdm(pool.imap(make_a_sample, arguments), total=iteration, desc="Making data"))
    return pd.DataFrame(rows)


def post_processing(dataset: pd.DataFrame) -> pd.DataFrame:
    std = lambda x: re.sub(r"[\t\n\r ]", "", x)
    dataset["std_func_body"] = dataset["func_body"].apply(std)
    dataset = dataset[dataset["std_func_body"] != ""]
    dataset.drop(columns=["std_func_body"], inplace=True)
    dataset.reset_index(drop=True, inplace=True)
    return dataset


def collect_java_file_urls(repos_directory: str) -> List[str]:
    cmd = f"""
    cd {repos_directory}
    find ~+ -type f -name *.java 
    """
    output = run(cmd, shell=True, capture_output=True, text=True).stdout
    java_file_urls = output.split('\n')[:-1]  # Remove the last element because it is the empty line for spacing in terminal 
    return java_file_urls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input")
    parser.add_argument("--dir", dest="dir")
    parser.add_argument("--output", dest="output")
    parser.add_argument("--workers", dest="workers")
    args = parser.parse_args()
    java_files = pd.read_parquet(args.input)
    java_files.reset_index(drop=True, inplace=True)
    df = make_dataset(java_files=java_files, repos_directory=args.dir, num_process=int(args.workers))
    df.to_parquet(args.output, "fastparquet")


if __name__ == "__main__":
    main()
    # with open("/var/data/lvdthieu/code-generation/java_data/AJavaFile.java", "r") as f:
    #     java_code = f.read()
    # print(java_code)
    # print("-" * 100)
    # print(get_functions(java_code))
 