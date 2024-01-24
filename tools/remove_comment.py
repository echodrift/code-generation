import pandas as pd


def find_comment(sol_file):
    sol_file = sol_file.replace("\r\n", "\n")
    state = "ETC"
    i = 0
    comments = []
    currentComment = None

    while i + 1 < len(sol_file):
        if state == "ETC" and sol_file[i] == "/" and sol_file[i + 1] == "/":
            state = "LINE_COMMENT"
            currentComment = {"type": "LineComment", "range": {"start": i}}
            i += 2
            continue

        if state == "LINE_COMMENT" and sol_file[i] == "\n":
            state = "ETC"
            currentComment["range"]["end"] = i
            comments.append(currentComment)
            currentComment = None
            i += 1
            continue

        if state == "ETC" and sol_file[i] == "/" and sol_file[i + 1] == "*":
            state = "BLOCK_COMMENT"
            currentComment = {"type": "BlockComment", "range": {"start": i}}
            i += 2
            continue

        if state == "BLOCK_COMMENT" and sol_file[i] == "*" and sol_file[i + 1] == "/":
            state = "ETC"
            currentComment["range"]["end"] = i + 2
            comments.append(currentComment)
            currentComment = None
            i += 2
            continue
        i += 1

    if currentComment and currentComment["type"] == "LineComment":
        if sol_file[i - 1] == "\n":
            currentComment["range"]["end"] = len(sol_file) - 1
        else:
            currentComment["range"]["end"] = len(sol_file)

        comments.append(currentComment)

    return comments


def remove_comment(sol_file):
    sol_file = sol_file.replace("\r\n", "\n")
    comments = find_comment(sol_file)
    removed_comment = ""
    begin = 0
    for comment in comments:
        removed_comment += sol_file[begin : comment["range"]["start"]]
        begin = comment["range"]["end"]
    removed_comment += sol_file[begin:]
    return removed_comment


if __name__ == "__main__":
    mask_entire_function_has_req = pd.read_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/data/only_mask_func_body.parquet",
        engine="fastparquet",
    )
    mask_entire_function_has_req[
        "func_body_removed_comment"
    ] = mask_entire_function_has_req["func_body"].apply(
        lambda source: remove_comment(source)
    )
    mask_entire_function_has_req.to_parquet(
        "/home/hieuvd/lvdthieu/CodeGen/data/data/only_mask_func_body.parquet",
        engine="fastparquet",
    )
