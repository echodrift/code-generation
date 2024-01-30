import pandas as pd



if __name__ == "__main__":
    # make_raw_test_suite(
    #     "/home/hieuvd/lvdthieu/CodeGen/data/test.jsonl",
    #     "/home/hieuvd/lvdthieu/CodeGen/data/raw_test_6k.parquet",
    # )
    split_test_suite(
        "/home/hieuvd/lvdthieu/CodeGen/data/test_suite_6k.parquet",
        "/home/hieuvd/lvdthieu/CodeGen/data/test/test_6k_v1"
    )
    # extract_error(
    #     "/home/hieuvd/lvdthieu/CodeGen/data/compile_info/test_6k/deepseek.parquet",
    #     "/home/hieuvd/lvdthieu/CodeGen/data/compile_info/test_6k/deepseek_v1.parquet"
    # )
