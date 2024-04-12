import argparse
import codecs

import pandas as pd
from make_data import get_functions, get_location
from tqdm import tqdm


def fill_file(row, generated_func_column: str, project_storage_url: str) -> str:
    """Fill generated code to file
    Args:
        row (pd.core.series.Series): Row
        generated_func_column (str): Generated function column
        project_storage_url (str): Project storage url

    Returns:
        str: Filled generated code to file
    """
    absolute_file_path = "{}/{}/{}".format(
        project_storage_url, row["proj_name"], row["relative_path"]
    )
    with codecs.open(absolute_file_path, "r", encoding="utf-8", errors="ignore") as f:
        original_file = f.read().replace("\r\n", "\n")
    filled_class = row["masked_class"].replace(
        "<FILL_FUNCTION_BODY>", row[generated_func_column]
    )
    # Find class in original file
    functions = get_functions(original_file)
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
            return filled_file
    return ""


def fill_generated_code_to_file(
    generated_func_dataset: pd.DataFrame,
    generated_func_column: str,
    project_storage_url: str,
) -> pd.DataFrame:
    """Fill generated code to file

    Args:
        generated_func_dataset (pd.DataFrame): Generated function dataset
        generated_func_column (str): Generated function column
        project_storage_url (str): Project storage url

    Returns:
        pd.DataFrame: Filled generated code to file
    """
    tqdm.pandas()
    generated_func_dataset["filled_file_" + generated_func_column] = (
        generated_func_dataset.progress_apply(fill_file, axis=1)
    )
    return generated_func_dataset


def main():
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--input", dest="input")
    args.add_argument("-o", "--output", dest="output")
    args.add_argument("-c", "--col", dest="col")
    args.add_argument("-d", "--dir", dest="dir")
    args = args.parse_args()
    df = pd.read_parquet(args.input, "fastparquet")
    new_df = fill_generated_code_to_file(
        generated_func_dataset=df,
        generated_func_column=args.col,
        project_storage_url=args.dir,
    )
    new_df.to_parquet(args.output, "fastparquet")


if __name__ == "__main__":
    main()
