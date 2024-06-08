import argparse
import logging
import os
import re

import pandas as pd
from antlr4 import *
from tqdm import tqdm


def modify_modifiers(code, class_name, method_name):
    message = ""
    lines_of_code = code.splitlines()
    for idx, line in enumerate(lines_of_code):
        if (
            line.strip().startswith("private")
            and "class" in line
            and class_name in line
        ):
            message += "<class_private> | "
            lines_of_code[idx] = line.replace("private", "public")
            message += (
                f"<modified_to \"{line.replace('private', 'public')}\"> | "
            )
        if (
            line.strip().startswith("protected")
            and "class" in line
            and class_name in line
        ):
            message += "<class_protected> | "
            lines_of_code[idx] = line.replace("protected", "public")
            message += (
                f"<modified_to \"{line.replace('protected', 'public')}\"> | "
            )
        if line.strip().startswith("class") and class_name in line:
            message += "<class_default> | "
            lines_of_code[idx] = "public " + line
            message += f'<modified_to "public {line}"> | '
        if line.strip().startswith("private") and method_name in line:
            message += "<func_private> | "
            lines_of_code[idx] = line.replace("private", "public")
            message += (
                f"<modified_to \"{line.replace('private', 'public')}\"> | "
            )
        if line.strip().startswith("protected") and method_name in line:
            message += "<func_protected> | "
            lines_of_code[idx] = line.replace("protected", "public")
            message += (
                f"<modified_to \"{line.replace('protected', 'public')}\"> | "
            )

    code = "\n".join(lines_of_code)
    return code, message


# # Read the Java source file
# with open('/data/hieuvd/lvdthieu/repos/tmp-projects/wkeyuan_DWSurvey/DWSurvey/src/main/java/net/diaowen/common/service/BaseServiceImpl.java', 'r') as file:
#     java_code = file.read()

# # Extract class and method modifiers
# code, message = modify_modifiers(java_code, "InputSentence", "doSomething")
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
            with open(
                path_to_file, "r", encoding="utf-8", errors="ignore"
            ) as f:
                code = f.read()
            code, message = modify_modifiers(
                code, row["class_name"], row["func_name"]
            )
            with open(
                path_to_file, "w", encoding="utf-8", errors="ignore"
            ) as f:
                f.write(code)
        except:
            logger.info(f"Failed {path_to_file}")
        else:
            if not message:
                message = "<no_change> |"
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
