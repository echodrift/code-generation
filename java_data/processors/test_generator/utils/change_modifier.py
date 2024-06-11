import argparse
import logging
import os
import re

import pandas as pd
from antlr4 import *
from tqdm import tqdm


def modify_modifiers(code, func_name):
    # message = []
    # lines_of_code = code.splitlines()
    # for idx, line in enumerate(lines_of_code):
    #     if line.strip().startswith("private "):
    #         lines_of_code[idx] = line.replace("private ", "")
    #         message.append(idx + 1)
    #     if line.strip().startswith("protected "):
    #         lines_of_code[idx] = line.replace("protected ", "")
    #         message.append(idx + 1)

    # code = "\n".join(lines_of_code)
    # if len(message) > 0:
    #     message = "Lines: " + ", ".join(map(str, message))
    # else:
    #     message = ""

    # New
    message = []
    lines_of_code = code.splitlines()
    class_pattern = r"(private|protected)\s+.*(class).*{"
    method_pattern = r"(private|protected)\s+.*\(.*\)\s*{"
    for idx, line in enumerate(lines_of_code):
        if re.search(class_pattern, line):
            lines_of_code[idx] = line.replace("private ", "").replace(
                "protected ", ""
            )
            message.append(idx + 1)
        if re.search(method_pattern, line) and func_name in line:
            lines_of_code[idx] = line.replace("private ", "public ").replace(
                "protected ", "public "
            )
            message.append(idx + 1)

    code = "\n".join(lines_of_code)
    if len(message) > 0:
        message = "Lines: " + ", ".join(map(str, message))
    else:
        message = ""
    return code, message


# # Read the Java source file
# # with open('/data/hieuvd/lvdthieu/repos/tmp-projects/wkeyuan_DWSurvey/DWSurvey/src/main/java/net/diaowen/common/service/BaseServiceImpl.java', 'r') as file:
# with open(
#     # "/data/hieuvd/lvdthieu/repos/tmp-projects/classgraph_classgraph/classgraph/src/main/java/nonapi/io/github/classgraph/utils/Assert.java"
#     "/home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/utils/InputSentence.java"
# ) as f:
#     java_code = f.read()

# # Extract class and method modifiers
# code, message = modify_modifiers(java_code)
# print(message)


# with open(
#     "/home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/utils/ModifiedInputSentence.java",
#     "w",
# ) as f:
#     f.write(code)


def main(args):
    df = pd.read_parquet(args.input)
    logger = logging.getLogger("change_modifier")
    logger.setLevel(logging.INFO)
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)
    logger.addHandler(
        logging.FileHandler(f"{args.log_dir}/change_modifier.log")
    )
    for _, row in tqdm(
        df.iterrows(), total=len(df), desc="Modifying modifiers"
    ):
        path_to_file = (
            f"{args.base_dir}/{row['proj_name']}/{row['relative_path']}"
        )
        try:
            with open(path_to_file, "r") as f:
                code = f.read()
            new_code, message = modify_modifiers(code, row["func_name"])
            with open(path_to_file, "w") as f:
                f.write(new_code)
        except:
            logger.info(f"Failed {path_to_file}")
        else:
            if not message:
                message = "<no_change>"
            logger.info(
                "{:<100}{:<20}{:<20}{}".format(
                    message, row["class_name"], row["func_name"], path_to_file
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input")
    parser.add_argument("--log-dir", dest="log_dir")
    parser.add_argument("--base-dir", dest="base_dir")
    args = parser.parse_args()
    main(args)
