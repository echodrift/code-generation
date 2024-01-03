import re
from enum import Enum
from typing import List, Optional, Tuple

from solidity_parser import parser


class State(Enum):
    DOUBLE_QUOTE = "double-quote-string-state"
    SINGLE_QUOTE = "single-quote-string-state"
    LINE_COMMENT = "line-comment-state"
    BLOCK_COMMENT = "block-comment-state"
    ETC = "etc-state"


class SolidityParser:
    """Solidity Parser class"""

    def __init__(self, contract: str):
        """Constructor of the class

        Args:
            contract (str): Solidity contract text
        """

        self.contract = contract

    def capture_comments(self) -> Optional[List[str]]:
        state = State.ETC
        i = 0
        comments = []
        currentComment = None

        while i + 1 < len(self.contract):
            if (
                state == State.ETC
                and self.contract[i] == "/"
                and self.contract[i + 1] == "/"
            ):
                state = State.LINE_COMMENT
                currentComment = {"type": "LineComment", "range": {"start": i}}
                i += 2
                continue

            if state == State.LINE_COMMENT and self.contract[i] == "\n":
                state = State.ETC
                currentComment["range"]["end"] = i
                comments.append(currentComment)
                currentComment = None
                i += 1
                continue

            if (
                state == State.ETC
                and self.contract[i] == "/"
                and self.contract[i + 1] == "*"
            ):
                state = State.BLOCK_COMMENT
                currentComment = {"type": "BlockComment", "range": {"start": i}}
                i += 2
                continue

            if (
                state == State.BLOCK_COMMENT
                and self.contract[i] == "*"
                and self.contract[i + 1] == "/"
            ):
                state = State.ETC
                currentComment["range"]["end"] = i + 2
                comments.append(currentComment)
                currentComment = None
                i += 2
                continue

            if state == State.ETC and self.contract[i] == '"':
                state = State.DOUBLE_QUOTE
                i += 1
                continue

            if (
                state == State.DOUBLE_QUOTE
                and self.contract[i] == '"'
                and (self.contract[i - 1] != "\\" or self.contract[i - 2] == "\\")
            ):
                state = State.ETC
                i += 1
                continue

            if state == State.ETC and self.contract[i] == "'":
                state = State.SINGLE_QUOTE
                i += 1
                continue

            if (
                state == State.SINGLE_QUOTE
                and self.contract[i] == "'"
                and (self.contract[i - 1] != "\\" or self.contract[i - 2] == "\\")
            ):
                state = State.ETC
                i += 1
                continue

            i += 1

        if currentComment and currentComment["type"] == "LineComment":
            if self.contract[i - 1] == "\n":
                currentComment["range"]["end"] = len(self.contract) - 1
            else:
                currentComment["range"]["end"] = len(self.contract)
            comments.append(currentComment)

        def normalize(sc: str, comments: List[dict]) -> List[dict]:
            for comment in comments:
                start = comment["range"]["start"] + 2
                end = (
                    comment["range"]["end"]
                    if comment["type"] == "LineComment"
                    else comment["range"]["end"] - 2
                )
                raw = sc[start:end]
                if comment["type"] == "BlockComment":
                    raw = "\n".join(
                        [
                            re.sub("/^\s*\*/", "", line.strip())
                            for line in raw.split("\n")
                        ]
                    ).strip()
                comment["content"] = raw
            return comments

        return normalize(self.contract, comments)

    def capture_functions(self) -> Optional[List[dict]]:
        functions = []
        try:
            sourceUnit = parser.parse(self.contract, loc=True)
            for child in sourceUnit["children"]:
                if child["type"] == "ContractDefinition":
                    for c in child["subNodes"]:
                        if c["type"] == "FunctionDefinition":
                            start, end = self.convert(self.contract, location=c["loc"])
                            content = "\n".join(
                                [
                                    line.strip()
                                    for line in self.contract[start:end].split("\n")
                                ]
                            )
                            functions.append(
                                {
                                    "range": {"start": start, "end": end},
                                    "content": content,
                                }
                            )
            return functions
        except:
            return None

    def convert(self, location: dict) -> List[int]:
        start_line = location["start"]["line"]
        start_col = location["start"]["column"]
        end_line = location["end"]["line"]
        end_col = location["end"]["column"]
        lines = self.contract.splitlines()
        start_idx = (
            sum([len(lines[i]) for i in range(start_line - 1)])
            + start_line
            - 1
            + start_col
        )
        end_idx = (
            sum([len(lines[i]) for i in range(end_line - 1)])
            + end_line
            - 1
            + end_col
            + 1
        )
        return [start_idx, end_idx]

    def get_pairs(self) -> List[Tuple[str]]:
        functions = self.capture_functions(self.contract)
        if functions:
            functions = sorted(functions, key=lambda x: x["range"]["start"])
        else:
            return None
        comments = self.capture_comments(self.contract)
        if comments:
            comments = sorted(comments, key=lambda x: x["range"]["start"])
        else:
            return None

        pairs = []
        last = 0
        for function in functions:
            comment_parts = []
            tmp = function["range"]["start"] - 1
            while self.contract[tmp] == " " or self.contract[tmp] == "\n":
                tmp -= 1
            for idx in range(last, len(comments)):
                if tmp in range(
                    comments[idx]["range"]["start"], comments[idx]["range"]["end"]
                ):
                    comment_parts.append(comments[idx]["content"])
                    cur = idx
                    prev = idx - 1
                    while True:
                        if prev < 0:
                            break
                        for i in range(
                            comments[prev]["range"]["end"] + 1,
                            comments[cur]["range"]["start"],
                        ):
                            if self.contract[i] not in [" ", "\n"]:
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
                pairs.append((function["content"], "\n".join(reversed(comment_parts))))
        return pairs
