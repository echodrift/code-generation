from antlr4 import *
from java.java8.JavaLexer import JavaLexer
from java.java8.JavaParser import JavaParser
from java.java8.JavaParserListener import JavaParserListener



# class LocationExtractor(JavaParserListener):
#     def __init__(self, token_stream):
#         super().__init__()
#         self.token_stream = token_stream

#     def print_location(self, ctx):
#         start_token = ctx.start
#         start_line = start_token.line
#         start_column = start_token.column
#         end_token = ctx.stop
#         end_line = end_token.line
#         end_column = end_token.column + len(end_token.text)

#         print(f"Name: {ctx.identifier().getText()}")
#         print(f"Start location: Line {start_line}, Column {start_column}")
#         print(f"End location: Line {end_line}, Column {end_column}")

#     def enterMethodDeclaration(self, ctx):
#         self.print_location(ctx)
    

# def main():
#     for proj in TEST_PROJ:
#         pass
#     java_code = """
# /*
# * Copyright (c) 2013-2017 Chris Newland.
# * Licensed under https://github.com/AdoptOpenJDK/jitwatch/blob/master/LICENSE-BSD
# * Instructions: https://github.com/AdoptOpenJDK/jitwatch/wiki
# */
# package org.adoptopenjdk.jitwatch.core;

# import static org.adoptopenjdk.jitwatch.core.JITWatchConstants.S_CLOSE_PARENTHESES;
# import static org.adoptopenjdk.jitwatch.core.JITWatchConstants.S_NEWLINE;
# import static org.adoptopenjdk.jitwatch.core.JITWatchConstants.S_OPEN_PARENTHESES;
# import static org.adoptopenjdk.jitwatch.core.JITWatchConstants.S_SPACE;

# import java.util.LinkedHashMap;
# import java.util.Map;

# public class ErrorLog
# {
#     private Map<String, Integer> errorCountMap = new LinkedHashMap<>();

#     public void clear()
#     {
#         errorCountMap.clear();
#     }

#     public void addEntry(String entry)
#     {
#         if (errorCountMap.containsKey(entry))
#         {
#             errorCountMap.put(entry, errorCountMap.get(entry) + 1);
#         }
#         else
#         {
#             errorCountMap.put(entry, 1);
#         }
#     }

#     @Override
#     public String toString()
#     {
#         StringBuilder builder = new StringBuilder();

#         for (Map.Entry<String, Integer> entry : errorCountMap.entrySet())
#         {
#             String msg = entry.getKey();
#             int count = entry.getValue();

#             if (count == 1)
#             {
#                 builder.append(msg).append(S_NEWLINE);
#             }
#             else
#             {
#                 builder.append(msg).append(S_SPACE).append(S_OPEN_PARENTHESES).append(count).append(S_SPACE).append("times").append(S_CLOSE_PARENTHESES).append(S_NEWLINE);
#             }
#         }

#         return builder.toString();

#     }
# }
#     """
#     input_stream = InputStream(java_code)
#     lexer = JavaLexer(input_stream)
#     token_stream = CommonTokenStream(lexer)
#     parser = JavaParser(token_stream)
#     tree = parser.compilationUnit()
#     # Create listener
#     listener = LocationExtractor(token_stream)

#     # Walk the parse tree
#     walker = ParseTreeWalker()
#     walker.walk(listener, tree)
def preprocess(java_file_urls_storage_url: str):
    with open(java_file_urls_storage_url, "r") as f:
        java_file_urls = list(map(lambda java_file_url: java_file_url[37:],f.readlines()))

if __name__ == "__main__":
    preprocess("/home/hieuvd/lvdthieu/CodeGen/crawler/java_file.txt")