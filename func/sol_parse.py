import re
from solidity_parser import parser
from typing import Optional

def capture_comments(url):
    with open(url, "r") as f:
        string = f.read()
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "" # so we will return empty to remove the comment
        else: # otherwise, we will return the 1st group
            return match.group(1) # captured quoted-string
    return regex.sub(_replacer, string)


def capture_functions(sc: str) -> Optional[str]:
    sourceUnit = parser.parse(sc, loc=True)
    for child in sourceUnit["children"]:
        if child["type"] == "ContractDefinition":
            for c in child["subNodes"]:
                if c["type"] == "FunctionDefinition":
                    print(get_string(sc, c["loc"]))


def get_string(sc: str, location: dict) -> str:
    start_line = location["start"]["line"]
    start_col = location["start"]["column"]
    end_line = location["end"]["line"]
    end_col = location["end"]["column"]
    lines = sc.splitlines()
    result = lines[start_line - 1][start_col:].strip() + '\n'
    result += '\n'.join([line.strip() for line in lines[start_line : end_line - 1]])
    result += '\n'
    result += lines[end_line - 1][:end_col + 1].strip()
    return result