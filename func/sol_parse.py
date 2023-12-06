import re
from solidity_parser import parser
from typing import Optional, List, Tuple
from enum import Enum


class State(Enum):
    DOUBLE_QUOTE = "double-quote-string-state"
    SINGLE_QUOTE = "single-quote-string-state"
    LINE_COMMENT = "line-comment-state"
    BLOCK_COMMENT = "block-comment-state"
    ETC = "etc-state"


def capture_comments(sc: str) -> Optional[List[str]]:
    state = State.ETC
    i = 0
    comments = []
    currentComment = None

    while (i + 1 < len(sc)):
        if (state == State.ETC and sc[i] == '/' and sc[i + 1] == '/'):
            state = State.LINE_COMMENT
            currentComment = {
                "type": "LineComment",
                "range": {"start": i}
            }
            i += 2
            continue
        
        if (state == State.LINE_COMMENT and sc[i] == '\n'):
            state = State.ETC
            currentComment["range"]["end"] = i
            comments.append(currentComment)
            currentComment = None
            i += 1
            continue

        if (state == State.ETC and sc[i] == '/' and sc[i + 1] == '*'):
            state = State.BLOCK_COMMENT
            currentComment = {
                "type": "BlockComment",
                "range": {"start": i}
            }
            i += 2
            continue;

        if (state == State.BLOCK_COMMENT and sc[i] == '*' and sc[i + 1] == '/'):
            state = State.ETC
            currentComment["range"]["end"] = i + 2
            comments.append(currentComment)
            currentComment = None
            i += 2
            continue

        if (state == State.ETC and sc[i] == '"'):
            state = State.DOUBLE_QUOTE
            i += 1
            continue

        if (state == State.DOUBLE_QUOTE and sc[i] == '"'
            and (sc[i - 1] != '\\' or sc[i - 2] == '\\')):
            state = State.ETC
            i += 1
            continue

        if (state == State.ETC and sc[i] == "'"):
            state = State.SINGLE_QUOTE
            i += 1
            continue

        if (state == State.SINGLE_QUOTE and sc[i] == "'"
            and (sc[i - 1] != '\\' or sc[i - 2] == '\\')):
            state = State.ETC
            i += 1
            continue

        i += 1
    
    if (currentComment and currentComment.type == "LineComment"):
        if (sc[i] == '\n'):
            currentComment["range"]["end"] = len(sc) - 1
        else:
            currentComment["range"]["end"] = len(sc)
        comments.append(currentComment)

    def normalize(sc: str, comments: List[dict]) -> List[dict]:
        for comment in comments:
            start = comment["range"]["start"] + 2
            end = comment["range"]["end"] if comment["type"] == "LineComment" else comment["range"]["end"] - 2
            raw = sc[start : end]
            if comment["type"] == "BlockComment":
                raw = '\n'.join([re.sub('/^\s*\*/', '', line.strip()) for line in raw.split('\n')]).strip()
            comment["content"] = raw
        return comments
    
    return normalize(sc, comments)


def capture_functions(sc: str) -> Optional[List[dict]]:
    functions = []
    try:
        sourceUnit = parser.parse(sc, loc=True)
        for child in sourceUnit["children"]:
            if child["type"] == "ContractDefinition":
                for c in child["subNodes"]:
                    if c["type"] == "FunctionDefinition":
                        start, end = convert(sc, location=c["loc"])
                        content = '\n'.join([line.strip() for line in sc[start:end].split('\n')])
                        functions.append({"range": {"start": start, "end": end}, "content": content})
        return functions
    except:
        return None
    
    
def convert(sc: str, location: dict) -> List[int]:
    start_line = location["start"]["line"]
    start_col = location["start"]["column"]
    end_line = location["end"]["line"]
    end_col = location["end"]["column"]
    lines = sc.splitlines()
    start_idx = sum([len(lines[i]) for i in range(start_line - 1)]) + start_line - 1 + start_col 
    end_idx = sum([len(lines[i]) for i in range(end_line - 1)]) + end_line - 1 + end_col + 1
    return [start_idx, end_idx]


def get_pairs(sc: str) -> List[Tuple[str]]:
    functions = capture_functions(sc)
    if functions:
        functions = sorted(functions, key=lambda x: x["range"]["start"])
    else:
        return None
    comments = capture_comments(sc)
    if comments:
        comments = sorted(comments, key=lambda x: x["range"]["start"])
    else:
        return None
    
    pairs = []
    last = 0
    for function in functions:
        comment_parts = []
        tmp = function["range"]["start"] - 1
        while sc[tmp] == ' ' or sc[tmp] == '\n': 
            tmp -= 1
        for idx in range(last, len(comments)):
            if tmp in range(comments[idx]["range"]["start"], comments[idx]["range"]["end"]):
                comment_parts.append(comments[idx]["content"])
                cur = idx
                prev = idx - 1
                while True:
                    if prev < 0:
                        break
                    for i in range(comments[prev]["range"]["end"] + 1, comments[cur]["range"]["start"]):
                        if sc[i] not in [' ', '\n']:
                            break
                    else:
                        comment_parts.append(comments[prev]["content"])
                        cur -= 1
                        prev -= 1
                        continue
                    break
                last = idx
                break
        if comment_parts:
            pairs.append((function["content"], '\n'.join(reversed(comment_parts))))
    return pairs



                


