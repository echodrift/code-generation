from antlr4 import *
from java.java8.JavaLexer import JavaLexer
from java.java8.JavaParser import JavaParser
from java.java8.JavaParserListener import JavaParserListener
import pandas as pd
import random
from typing import Tuple, Optional
from collections import namedtuple
from tqdm import tqdm

random.seed(0)
ASample = namedtuple("ASample", "class_name func_name masked_class func_body")
Location = namedtuple("Location", "start_line start_col end_line end_col")

class Extractor(JavaParserListener):
    def __init__(self, token_stream):
        super().__init__()
        self.functions = []
        self.token_stream = token_stream
    
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


def mask_function(java_code: str) -> Optional[ASample]:
    input_stream = InputStream(java_code)
    lexer = JavaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()
    # Create listener
    listener = Extractor(token_stream)
    # Walk the parse tree
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    functions = listener.get_function()

    # If file has no function, return None
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


def make_dataset(java_file_urls_storage_url: str) -> pd.DataFrame:
    rows = []
    with open(java_file_urls_storage_url, "r") as f:
        java_file_urls = map(lambda url: url.strip(), f.readlines())
    
    for java_file_url in tqdm(java_file_urls):
        project_name = java_file_url[37:].split('/')[0]
        relative_path = '/'.join(java_file_url[37:].split('/')[1:])
        with open(java_file_url, "r") as f:
            java_code = f.read()
            sample = mask_function(java_code)
            if sample:
                rows.append({
                    "proj_name": project_name,
                    "relative_path": relative_path,
                    "class_name": sample.class_name,
                    "func_name": sample.func_name,
                    "masked_class": sample.masked_class,
                    "func_body": sample.func_body
                })
    return pd.DataFrame(rows)
    


if __name__ == "__main__":
    df = make_dataset("/home/hieuvd/lvdthieu/CodeGen/crawler/java_file.txt")
    df.to_parquet("dataset.parquet", "fastparquet")