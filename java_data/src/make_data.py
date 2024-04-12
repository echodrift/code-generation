import argparse
import codecs
import random
import re
from typing import List, NamedTuple, Optional, Tuple

import pandas as pd
from antlr4 import *
from src.java.java8.JavaLexer import JavaLexer
from src.java.java8.JavaParser import JavaParser
from src.java.java8.JavaParserListener import JavaParserListener
from tqdm import tqdm

ASample = NamedTuple(
    "ASample",
    [
        ("class_name", str),
        ("func_name", str),
        ("masked_class", str),
        ("func_body", str),
    ],
)
Location = NamedTuple(
    "Location",
    [("start_line", int), ("start_col", int), ("end_line", int), ("end_col", int)],
)
Function = NamedTuple(
    "Function",
    [
        ("class_name", str),
        ("class_loc", Location),
        ("func_name", str),
        ("func_body_loc", Location),
    ],
)


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
        if ctx.typeTypeOrVoid() == "void":
            return
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

    def get_function(self):
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
        functions = listener.get_function()
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

    # Randomly select a function
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


def make_dataset(
    java_file_urls_storage_url: str,
    repos_directory: str = "/var/data/lvdthieu/repos/maven_projects/",
    checkpoint: str = "",
) -> pd.DataFrame:
    """Make dataset

    Args:
        java_file_urls_storage_url (str): url to file that contain java file urls
        repos_directory (str): path to diretory of repositories. Default to "/var/data/lvdthieu/repos/maven_projects/"
        checkpoint (str, optional): where to store checkpoint of process. Defaults to "".

    Returns:
        pd.DataFrame: Dataset
    """
    rows = []
    with open(java_file_urls_storage_url, "r") as f:
        java_file_urls = list(
            map(lambda url: url.replace(repos_directory, ""), f.read().split("\n"))
        )

    for java_file_url in tqdm(java_file_urls):

        project_name = java_file_url.split("/")[0]
        relative_path = "/".join(java_file_url.split("/")[1:])
        with codecs.open(java_file_url, "r", encoding="utf-8", errors="ignore") as f:
            try:
                java_code = f.read()
                # sample = mask_function(java_code)
                sample = modified_mask_function(java_code)
                if sample:
                    rows.append(
                        {
                            "proj_name": project_name,
                            "relative_path": relative_path,
                            "class_name": sample.class_name,
                            "func_name": sample.func_name,
                            "masked_class": sample.masked_class,
                            "func_body": sample.func_body,
                        }
                    )
            except:
                pass
        if checkpoint:
            if rows and len(rows) % 1000 == 0:
                pd.DataFrame(rows).to_parquet(checkpoint, "fastparquet")
    return pd.DataFrame(rows)


def post_processing(dataset: pd.DataFrame) -> pd.DataFrame:
    std = lambda x: re.sub(r"[\t\n\r ]", "", x)
    dataset["std_func_body"] = dataset["func_body"].apply(std)
    dataset = dataset[dataset["std_func_body"] != ""]
    dataset.drop(columns=["std_func_body"], inplace=True)
    dataset.reset_index(drop=True, inplace=True)
    return dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-c", "--check", dest="checkpoint")
    args = parser.parse_args()
    df = post_processing(
        make_dataset(java_file_urls_storage_url=args.input, checkpoint=args.checkpoint)
    )
    df.to_parquet(args.output, "fastparquet")


if __name__ == "__main__":
    main()
