from antlr4 import *
from java.java8.JavaLexer import JavaLexer
from java.java8.JavaParser import JavaParser
from java.java8.JavaParserListener import JavaParserListener
import pandas as pd
import random
from typing import Tuple, Optional, List, NamedTuple
from collections import namedtuple, defaultdict
from tqdm import tqdm
import codecs
import argparse
import re


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


class ExtractParentComponent(JavaParserListener):
    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name
        self.parent_class = None

    def enterClassDeclaration(self, ctx):
        if self.class_name == ctx.identifier().getText():
            if ctx.typeType():
                self.parent_class = ctx.typeType().getText()

    def get_parent_class(self):
        return self.parent_class

   
class ExtractSignatureAndVar(JavaParserListener):
    def __init__(self):
        super().__init__()
        self.class_comp = defaultdict(list)
    
    def enterClassDeclaration(self, ctx):
        self.class_name = ctx.identifier().getText()

    def enterMethodDeclaration(self, ctx):
        self.func_name = ctx.identifier().getText()
        body = ctx.methodBody().block()
        func_body_start_idx, _ = get_location(Location(body.start.line, body.start.column, 
                                                       body.stop.line, body.stop.column + len(body.stop.text)))
        func_start_idx, _ = get_location(Location(ctx.start.line, ctx.start.column,
                                                  ctx.stop.line, ctx.stop.column + len(ctx.stop.text)))
        self.class_comp[self.class_name].append((func_start_idx, func_body_start_idx))
    
    def enterVariableDeclaratorId(self, ctx: VariableDeclaratorIdContext):
        return super().enterVariableDeclaratorId(ctx)

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


def extract_parent_component(java_code: str, proj_name: str, class_name: str):
    # parsed_file = file_url.replace(".txt", ".json")
    # with open(parsed_file, "r") as f:
    #     ast = json.load(f)
    # super_class_name = None
    # for cls in ast["types"]:
    #     if not cls["interface"] and cls["name"]["identifier"] == class_name:
    #         if cls["superclassType"]:
    #             super_class_name = cls["superclassType"]["name"]["identifier"]
    #             break
    # else:
    #     return None
    # try:
        input_stream = InputStream(java_code)
        lexer = JavaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = JavaParser(token_stream)
        tree = parser.compilationUnit()
        # Create listener
        listener = ExtractParentComponent(class_name)
        # Walk the parse tree
        walker = ParseTreeWalker()
        walker.walk(listener, tree)
        parent = listener.get_parent_class()
        
        if not parent:
            return ""
        else:
            pass


def get_signature_component(java_code: str):
    input_stream = InputStream(java_code)
    lexer = JavaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()
    # Create listener
    listener = ExtractSignatureAndVar()
    # Walk the parse tree
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    class_comps = listener.get_class_comp()
    print(class_comps)
    
        
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
        case "md":
            df = post_processing(make_dataset(java_file_urls_storage_url=args.input, checkpoint=args.checkpoint))
            df.to_parquet(args.output, "fastparquet")
        case "ff":
            df = pd.read_parquet(args.input, "fastparquet")
            df = fill_generated_code_to_file(df, args.col, args.dir)
            df.to_parquet(args.output, "fastparquet")
        case "epc":
            java_code = \
"""
/*******************************************************************************
 *     ___                  _   ____  ____
 *    / _ \ _   _  ___  ___| |_|  _ \| __ )
 *   | | | | | | |/ _ \/ __| __| | | |  _ \
 *   | |_| | |_| |  __/\__ \ |_| |_| | |_) |
 *    \__\_\\__,_|\___||___/\__|____/|____/
 *
 *  Copyright (c) 2014-2019 Appsicle
 *  Copyright (c) 2019-2023 QuestDB
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 ******************************************************************************/

package io.questdb.cairo.frm.file;

import io.questdb.cairo.CairoConfiguration;
import io.questdb.cairo.ColumnType;
import io.questdb.cairo.frm.FrameColumn;
import io.questdb.cairo.frm.FrameColumnPool;
import io.questdb.cairo.frm.FrameColumnTypePool;
import io.questdb.std.FilesFacade;
import io.questdb.std.ObjList;
import io.questdb.std.str.Path;

import java.io.Closeable;

public class ContiguousFileColumnPool implements FrameColumnPool, Closeable {
    private final ColumnTypePool columnTypePool = new ColumnTypePool();
    private final CairoConfiguration configuration;
    private final FilesFacade ff;
    private final ListPool<ContiguousFileFixFrameColumn> fixColumnPool = new ListPool<>();
    private final ListPool<ContiguousFileFixFrameColumn> indexedColumnPool = new ListPool<>();
    private final ListPool<ContiguousFileVarFrameColumn> varColumnPool = new ListPool<>();
    private boolean canWrite;
    private boolean isClosed;

    public ContiguousFileColumnPool(CairoConfiguration configuration) {
        this.ff = configuration.getFilesFacade();
        this.configuration = configuration;
    }

    @Override
    public void close() {
        this.isClosed = true;
    }

    @Override
    public FrameColumnTypePool getPoolRO(int columnType) {
        this.canWrite = false;
        return columnTypePool;
    }

    @Override
    public FrameColumnTypePool getPoolRW(int columnType) {
        this.canWrite = true;
        return columnTypePool;
    }

    private class ColumnTypePool implements FrameColumnTypePool {

        @Override
        public FrameColumn create(
                Path partitionPath,
                CharSequence columnName,
                long columnTxn,
                int columnType,
                int indexBlockCapacity,
                long columnTop,
                int columnIndex,
                boolean isEmpty
        ) {
            boolean isIndexed = indexBlockCapacity > 0;

            if (ColumnType.isVarSize(columnType)) {
                ContiguousFileVarFrameColumn column = getVarColumn();
                if (canWrite) {
                    column.ofRW(partitionPath, columnName, columnTxn, columnType, columnTop, columnIndex);
                } else {
                    column.ofRO(partitionPath, columnName, columnTxn, columnType, columnTop, columnIndex, isEmpty);
                }
                return column;
            }

            if (columnType == ColumnType.SYMBOL) {
                if (canWrite && isIndexed) {
                    ContiguousFileIndexedFrameColumn indexedColumn = getIndexedColumn();
                    indexedColumn.ofRW(partitionPath, columnName, columnTxn, columnType, indexBlockCapacity, columnTop, columnIndex, isEmpty);
                    return indexedColumn;
                }
            }

            ContiguousFileFixFrameColumn column = getFixColumn();
            if (canWrite) {
                column.ofRW(partitionPath, columnName, columnTxn, columnType, columnTop, columnIndex);
            } else {
                column.ofRO(partitionPath, columnName, columnTxn, columnType, columnTop, columnIndex, isEmpty);
            }
            return column;
        }

        private ContiguousFileFixFrameColumn getFixColumn() {
            if (fixColumnPool.size() > 0) {
                return fixColumnPool.pop();
            }
            ContiguousFileFixFrameColumn col = new ContiguousFileFixFrameColumn(configuration);
            col.setPool(fixColumnPool);
            return col;
        }

        private ContiguousFileIndexedFrameColumn getIndexedColumn() {
            if (indexedColumnPool.size() > 0) {
                return (ContiguousFileIndexedFrameColumn) indexedColumnPool.pop();
            }
            ContiguousFileIndexedFrameColumn col = new ContiguousFileIndexedFrameColumn(configuration);
            col.setPool(indexedColumnPool);
            return col;
        }

        private ContiguousFileVarFrameColumn getVarColumn() {
            if (varColumnPool.size() > 0) {
                return varColumnPool.pop();
            }
            ContiguousFileVarFrameColumn col = new ContiguousFileVarFrameColumn(configuration);
            col.setPool(varColumnPool);
            return col;
        }
    }

    private class ListPool<T> implements RecycleBin<T> {
        private final ObjList<T> pool = new ObjList<>();

        @Override
        public boolean isClosed() {
            return isClosed;
        }

        public T pop() {
            T last = pool.getLast();
            pool.setPos(pool.size() - 1);
            return last;
        }

        @Override
        public void put(T frame) {
            pool.add(frame);
        }

        public int size() {
            return pool.size();
        }
    }
}
"""
            get_signature_component(java_code)