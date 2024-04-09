import argparse
import json
from collections import defaultdict

import pandas as pd
from antlr4 import *
from java.java8.JavaLexer import JavaLexer
from java.java8.JavaParser import JavaParser
from java.java8.JavaParserListener import JavaParserListener
from make_data import Location, get_location
from tqdm import tqdm


class ExtractSignatureAndVar(JavaParserListener):
    """Extract signature and variables in a class"""

    def __init__(self, java_code: str):
        """Constructor

        Args:
            java_code (str): Java code
        """
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


def extract_signature_and_var(java_code: str):
    """Extract signature and variables in a class

    Args:
        java_code (str): Java code

    Returns:
        str: Signature and variables
    """
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


def get_parent_class(row, storage_url: str):
    """Get parent class in a class
    Args:
        row (pd.DataFrame): Dataset
        storage_url (str): Storage url  

    Returns:
        str: Parent class
    """
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
    

def get_parent_signature_and_var(df: pd.DataFrame, storage_url: str) -> pd.DataFrame:
    """Get parent signature and variables in a class
    Args:
        df (pd.DataFrame): Dataset
        storage_url (str): Storage url  

    Returns:
        pd.DataFrame: Dataset with parent signature and variables
    """
    tqdm.pandas()
    df["parent_class_code"] = df.progress_apply(lambda row: get_parent_class(row, storage_url), axis=1)
    df["inherit_elements"] = df["parent_class_code"].apply(extract_signature_and_var)
    return df


def main():
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--input", dest="input")
    args.add_argument("-o", "--output", dest="output")
    args.add_argument("-d", "--dir", dest="dir", help="Directoriy of parsed projects (json files)")
    args = args.parse_args()
    df = pd.read_parquet(args.input, "fastparquet")
    new_df = get_parent_signature_and_var(df=df, storage_url=args.dir)
    new_df.to_parquet(args.output, "fastparquet")



