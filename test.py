# import re

# string = "uint"

# if re.fullmatch(r"(uint)\d*", string):
#     print("True")
# else:
#     print("False")

from solidity_parser import parser
import json

with open("/home/lvdthieu/Documents/Projects/CodeGen/data/sol/DummyTel.sol", "r") as f:
    contract = f.read()

sourceUnit = parser.parse(contract, loc=False)
sourceUnit = json.dumps(sourceUnit, indent=4)

with open("test.json", "w") as f:
    f.write(sourceUnit)