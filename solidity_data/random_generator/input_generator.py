import math
import random
from enum import Enum
from typing import List

random.seed = 10


class AddressGenerator:
    addresses = [
        "0xca35b7d915458ef540ade6068dfe2f44e8fa733c",
        "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c",
        "0x4b0897b0513fdc7c541b6d9d7e929c4e5364d2db",
        "0x583031d1113ad414f02576bd6afabfb302140225",
        "0xdd870fa1b7c4700f2bd7f44238821c26f7392148",
    ]

    def address_generate(self) -> str:
        rand_idx = random.randint(0, 4)
        return self.addresses[rand_idx]

    def address_list(self) -> List[str]:
        return self.addresses


class BooleanGenerator:
    def bool_generate(self) -> bool:
        return bool(random.getrandbits(1))

    def bool_array_generate(self, len: int) -> List[bool]:
        list_bool = []
        for _ in range(len):
            list_bool.append(self.bool_generate())
        return list_bool


class ByteGenerator:
    def byte_generate(self):
        pass


class IntegerGenerator:
    def integer_generate(self, int_type: str) -> int:
        int_type = int_type.split("int")
        rand_num = 0
        if not int_type[1]: 
            int_type[1] = 256
        else:
            int_type[1] = int(int_type[1])
        
        if not int_type[0]:
            rand_num = random.randint(-math.pow(2, int_type[1] - 1), math.pow(2, int_type[1] - 1) - 1)
        else:
            rand_num = random.randint(0, math.pow(2, int_type[1]) - 1)
        
        return str(rand_num)

    def integer_array_generate(self, int_type: str, len: int) -> List[int]:
        list_int = []
        for _ in range(len):
            list_int.append(self.integer_generate(int_type))
        return list_int
    

class StringGenerator:
    def string_generate(self, string_len: int, letters=[]) -> str:
        if not letters:
            string = []
            for _ in range(string_len):
                string.append(chr(random.randint(32, 126)))
        else:
            string = random.choices(letters, k=string_len)

        return "".join(string)

    def string_array_generate(
        self, string_lens: List[int], len: int, letters=[]
    ) -> List[str]:
        strings = []
        for i in range(len):
            strings.append(self.string_generate(string_lens[i], letters))

        return strings
