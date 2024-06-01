import codecs
import re

import pandas as pd
from make_data.make_data import get_functions, get_location
from tqdm import tqdm


def fill_file(
    row,
    proj_storage_dir="/home/hieuvd/lvdthieu/repos/tmp-projects",
    column_to_check="generated_code",
):
    if row["compiler_feedback"] == "<success>":
        return "<success>"
    elif row["compiler_feedback"] == "<execute_error>":
        with open("/home/hieuvd/lvdthieu/code.log", "a") as f:
            f.write(row["relative_path"] + "\n")
            f.write("-" * 100 + "\n")
        return "<execute_error>"
    else:
        absolute_file_path = "{}/{}/{}".format(
            proj_storage_dir, row["proj_name"], row["relative_path"]
        )
        with codecs.open(
            absolute_file_path, "r", encoding="utf-8", errors="ignore"
        ) as f:
            original_file = f.read().replace("\r\n", "\n")
        filled_class = row["masked_class"].replace(
            "<FILL_FUNCTION_BODY>", row[column_to_check]
        )
        # Find class in original file
        functions = get_functions(original_file)
        if functions:
            for function in functions:
                if (
                    function["class_name"] == row["class_name"]
                    and function["func_name"] == row["func_name"]
                ):
                    class_start_idx, class_end_idx = get_location(
                        original_file, function["class_loc"]
                    )
                    filled_file = (
                        original_file[:class_start_idx]
                        + filled_class
                        + original_file[class_end_idx:]
                    )
                    errors = list(set(row["compiler_feedback"].split("\n")))
                    new_errors = []
                    for error in errors:
                        try:
                            file, line, col, err = re.search(
                                r"<file>(.*?)<line>(\d+)<col>(\d+)<err>(.*)",
                                error,
                            ).groups()
                            if (
                                file
                                == row["proj_name"] + "/" + row["relative_path"]
                            ):
                                lines_of_code = filled_file.splitlines() + [""]
                                line_of_code = lines_of_code[int(line) - 1]
                                new_errors.append(
                                    f"<file>{file}<line>{line}<col>{col}<line_of_code>{line_of_code}<err>{err}"
                                )
                            else:
                                new_errors.append(error)
                        except:
                            with open(
                                "/home/hieuvd/lvdthieu/code.log", "a"
                            ) as f:
                                f.write(row["relative_path"] + "\n")
                                f.write("-" * 100 + "\n")
                    return "\n".join(new_errors)
            return None
        else:
            return None


if __name__ == "__main__":
    valid_finetune = pd.read_parquet(
        "/home/hieuvd/lvdthieu/valid_finetune_compiled_v1.parquet"
    )
    new_compiler_feedback = []
    for _, row in tqdm(
        valid_finetune.iterrows(),
        total=len(valid_finetune),
        desc="Getting line",
    ):
        new_compiler_feedback.append(fill_file(row))

    valid_finetune["new_compiler_feedback"] = new_compiler_feedback
    valid_finetune.to_parquet(
        "/home/hieuvd/lvdthieu/valid_finetune_compiled_v2.parquet"
    )
    valid_finetune.sample(n=100).to_csv("/home/hieuvd/lvdthieu/check.csv")
