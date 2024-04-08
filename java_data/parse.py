import argparse
import codecs
import json
import random
import re
from collections import defaultdict
from typing import List, NamedTuple, Optional, Tuple

import pandas as pd
from antlr4 import *
from java.java8.JavaLexer import JavaLexer
from java.java8.JavaParser import JavaParser
from java.java8.JavaParserListener import JavaParserListener
from tqdm import tqdm


ASample = NamedTuple("ASample", [("class_name", str), ("func_name", str), ("masked_class", str), ("func_body", str)])
Location = NamedTuple("Location", [("start_line", int), ("start_col", int), ("end_line", int), ("end_col", int)])
Function = NamedTuple("Function", [("class_name", str), ("class_loc", Location), ("func_name", str), ("func_body_loc", Location)])


class ExtractFunc(JavaParserListener):
    def __init__(self):
        super().__init__()
        self.functions = []
    
    def enterClassDeclaration(self, ctx):
        self.class_name = ctx.identifier().getText()
        self.class_loc = Location(ctx.start.line, ctx.start.column, ctx.stop.line, 
                                  ctx.stop.column + len(ctx.stop.text))

    def enterMethodDeclaration(self, ctx):
        self.func_name = ctx.identifier().getText()
        body = ctx.methodBody().block()
        if not body:
            return
        self.func_body_loc = Location(body.start.line, body.start.column, 
                                      body.stop.line, body.stop.column + len(body.stop.text))
        try:
            self.functions.append({"class_name": self.class_name, 
                                "class_loc": self.class_loc,
                                "func_name": self.func_name,
                                "func_body_loc": self.func_body_loc})
        except:
            pass
                            
    def get_function(self):
        return self.functions


class ExtractSignatureAndVar(JavaParserListener):
    def __init__(self, java_code: str):
        super().__init__()
        self.class_comp = defaultdict(list)
        self.java_code = java_code

    def enterClassDeclaration(self, ctx):
        self.class_name = ctx.identifier().getText()

    def enterMethodDeclaration(self, ctx):
        self.func_name = ctx.identifier().getText()
        body = ctx.methodBody().block()
        func_body_start_idx, _ = get_location(self.java_code, Location(body.start.line, body.start.column, 
                                                       body.stop.line, body.stop.column + len(body.stop.text)))
        func_start_idx, _ = get_location(self.java_code, Location(ctx.start.line, ctx.start.column,
                                                  ctx.stop.line, ctx.stop.column + len(ctx.stop.text)))
        self.class_comp[self.class_name].append(self.java_code[func_start_idx : func_body_start_idx])
    
    def enterFieldDeclaration(self, ctx):
        variable_name = ctx.variableDeclarators().getText()
        variable_type = ctx.typeType().getText()
        self.class_comp[self.class_name].append("%s %s;" % (variable_type, variable_name))

    def get_class_comp(self):
        return self.class_comp


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
    class_start_idx, class_end_idx = get_location(java_code, random_function["class_loc"])
    func_body_start_idx, func_body_end_idx = get_location(java_code, random_function["func_body_loc"])
    masked_class = java_code[class_start_idx : func_body_start_idx + 1] + "<FILL_FUNCTION_BODY>" \
                    + java_code[func_body_end_idx - 1 : class_end_idx]
    func_body = java_code[func_body_start_idx + 1 : func_body_end_idx - 1]

    return ASample(class_name=random_function["class_name"], 
                   func_name=random_function["func_name"], 
                   masked_class=masked_class, 
                   func_body=func_body)


def modified_mask_function(java_code: str) -> Optional[ASample]:
    functions = get_functions(java_code)
    if not functions:
        return None
    # Randomly select a function
    def get_len(java_code: str, loc: Location) -> int:
        start_idx, end_idx = get_location(java_code, loc)
        return end_idx - start_idx
    
    functions_with_len_body = [[get_len(java_code, func["func_body_loc"]), func] for func in functions]
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
    class_start_idx, class_end_idx = get_location(java_code, random_function["class_loc"])
    func_body_start_idx, func_body_end_idx = get_location(java_code, random_function["func_body_loc"])
    masked_class = java_code[class_start_idx : func_body_start_idx + 1] + "<FILL_FUNCTION_BODY>" \
                    + java_code[func_body_end_idx - 1 : class_end_idx]
    func_body = java_code[func_body_start_idx + 1 : func_body_end_idx - 1]

    return ASample(class_name=random_function["class_name"], 
                   func_name=random_function["func_name"], 
                   masked_class=masked_class, 
                   func_body=func_body)


def make_dataset(java_file_urls_storage_url: str, checkpoint: str="") -> pd.DataFrame:
    rows = []
    with open(java_file_urls_storage_url, "r") as f:
        java_file_urls = list(map(lambda url: url.strip(), f.readlines()))
    
    for java_file_url in tqdm(java_file_urls):
        project_name = java_file_url[37:].split('/')[0]
        relative_path = '/'.join(java_file_url[37:].split('/')[1:])
        with codecs.open(java_file_url, "r", encoding="utf-8", errors="ignore") as f:
            try:
                java_code = f.read()
                # sample = mask_function(java_code)
                sample = modified_mask_function(java_code)
                if sample:
                    rows.append({
                        "proj_name": project_name,
                        "relative_path": relative_path,
                        "class_name": sample.class_name,
                        "func_name": sample.func_name,
                        "masked_class": sample.masked_class,
                        "func_body": sample.func_body
                    })
            except:
                pass
        if checkpoint:
            if rows and len(rows) % 1000 == 0:
                pd.DataFrame(rows).to_parquet(checkpoint, "fastparquet")
    return pd.DataFrame(rows)


def post_processing(dataset: pd.DataFrame) -> pd.DataFrame:
    std = lambda x: re.sub(r'[\t\n\r ]', '', x)
    dataset["std_func_body"] = dataset["func_body"].apply(std)
    dataset = dataset[dataset["std_func_body"] != ""]
    dataset.drop(columns=["std_func_body"], inplace=True)
    dataset.reset_index(drop=True, inplace=True)
    return dataset


def fill_generated_code_to_file(generated_func_dataset: pd.DataFrame, 
                                generated_func_column: str, 
                                project_storage_url: str) -> pd.DataFrame:
    tqdm.pandas()
    def fill_file(row):
        absolute_file_path = "{}/{}/{}".format(project_storage_url, row["proj_name"], row["relative_path"])
        with codecs.open(absolute_file_path, "r", encoding="utf-8", errors="ignore") as f:
            original_file = f.read().replace("\r\n", "\n")
        filled_class = row["masked_class"].replace("<FILL_FUNCTION_BODY>", row[generated_func_column])
        # Find class in original file
        functions = get_functions(original_file)
        for function in functions:
            if function["class_name"] == row["class_name"] and function["func_name"] == row["func_name"]:
                class_start_idx, class_end_idx = get_location(original_file, function["class_loc"])
                filled_file = original_file[:class_start_idx] + filled_class + original_file[class_end_idx:]
                return filled_file
        return ""
    
    generated_func_dataset["filled_file_" + generated_func_column] = generated_func_dataset.progress_apply(fill_file, axis=1)

    return generated_func_dataset


def search_parent_class(df: pd.DataFrame, storage_url: str) -> pd.DataFrame:
    def get_parent_class(row, storage_url: str):
        parsed_project_path = "{}/parsed_{}.json".format(storage_url, row["proj_name"])
        with open(parsed_project_path, "r") as f:
            class_info = json.load(f)
        for cls in class_info:
            if (cls["classInfos"]["filePath"] == "{}/{}".format(row["proj_name"], row["relative_path"]) and
                cls["classInfos"]["className"] == row["class_name"]):
                if cls["classInfos"]["extendedClassQualifiedName"] not in ["", "java.lang.Object"]:
                    parent_class = cls["classInfos"]["extendedClassQualifiedName"]
                else:
                    parent_class = ""
                break
        else:
            parent_class = ""
        
        if parent_class == "":
            return ""
        else:
            for cls in class_info:
                if (cls["classInfos"]["QualifiedName"] == parent_class):
                    return cls["classInfos"]["sourceCode"]
            return ""
    tqdm.pandas()
    df["parent_class_code"] = df.progress_apply(lambda row: get_parent_class(row, storage_url), axis=1)
    return df


def extract_signature_and_var(java_code: str):
    if not java_code:
        return ""
    input_stream = InputStream(java_code)
    lexer = JavaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()
    # Create listener
    listener = ExtractSignatureAndVar(java_code)
    # Walk the parse tree
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    class_comps = listener.get_class_comp()
    return json.dumps(class_comps)


def get_parent_signature_and_var(df: pd.DataFrame, storage_url: str) -> pd.DataFrame:
    new_df = search_parent_class(df, storage_url)
    new_df["inherit_elements"] = new_df["parent_class_code"].apply(extract_signature_and_var)
    return new_df


def store_dataset(df: pd.DataFrame, storage_url: str):
    df.to_parquet(storage_url, "fastparquet")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-c", "--check", dest="checkpoint")
    parser.add_argument("-f", "--func", dest="func")
    parser.add_argument("-d", "--dir", dest="dir")
    parser.add_argument("--col", dest="col")
    args = parser.parse_args()
    
    match args.func:
        case "md":  # Make Dataset
            df = post_processing(make_dataset(java_file_urls_storage_url=args.input, checkpoint=args.checkpoint))
            store_dataset(df, args.output)
        case "ff":  # Fill Generated Code
            df = pd.read_parquet(args.input, "fastparquet")
            df = fill_generated_code_to_file(df, args.col, args.dir)
            store_dataset(df, args.output)
        case "epc":  # Extract Parent Component
            df = pd.read_parquet(args.input, "fastparquet")
            new_df = get_parent_signature_and_var(df, args.dir)
            store_dataset(new_df, args.output)