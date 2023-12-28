import json
from collections import defaultdict
from typing import Dict, List, Tuple, TypeVar

from solidity_parser import parser
import re
from func.input_generator import IntegerGenerator, StringGenerator, BooleanGenerator, ByteGenerator, AddressGenerator

TypeName = TypeVar("TypeName")
Name = TypeVar("Name")
ParamValue = TypeVar("ParamValue")
VarType = TypeVar("VarType")


class ParamGenerator:
    def __init__(self, contract: str):
        self.contract = contract
        self.ig = IntegerGenerator()
        self.sg = StringGenerator()
        self.bg = BooleanGenerator()
        self.byteg = ByteGenerator()
        self.ag = AddressGenerator()

    def _get_params(
        self, contract_name: str, function_name: str
    ) -> Dict[VarType, List[Tuple[TypeName, Name]]]:
        sourceUnit = parser.parse(self.contract, loc=False)
        params = defaultdict(list)
        for child in sourceUnit["children"]:
            if child["type"] == "ContractDefinition":
                if child["name"] == contract_name:
                    for c in child["subNodes"]:
                        if c["type"] == "FunctionDefinition":
                            if c["name"] == function_name:
                                for param in c["parameters"]["parameters"]:
                                    variable_type = param["typeName"]["type"]
                                    if variable_type == "ElementaryTypeName":
                                        typename = param["typeName"]["name"]
                                        name = param["name"]
                                        params[variable_type].append((typename, name))
                                    else:
                                        pass
                                break
        return params

    def generate_input(
        self, contract_name: str, function_name: str
    ) -> List[ParamValue]:
        params = self._get_params(contract_name, function_name)
        inputs = []
        for var_type in params:
            if var_type == "ElementaryTypeName":
                for param in params[var_type]:
                    if re.fullmatch(r"(uint)\d*", param[0]) or re.fullmatch(r"(int)\d*", param[0]):
                        inputs.append((param[1], self.ig.integer_generate(param[0])))
                    elif param[0] == "bool":
                        inputs.append((param[1], self.bg.bool_generate()))
                    elif param[0] == "address":
                        inputs.append((param[1], self.ag.address_generate()))
                    elif param[0] == "string":
                        inputs.append((param[1], self.sg.string_generate(10)))
                    else:
                        pass
            else:
                pass
        return inputs

