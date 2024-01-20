import pandas as pd
from subprocess import run
import argparse
import os

# import re
# ERROR = [
#     "ParserError",
#     "DocstringParsingError",
#     "SyntaxError",
#     "DeclarationError",
#     "TypeError",
#     "UnimplementedFeatureError",
# ]


# def initial(test_source):
#     test = pd.read_parquet(test_source, engine="fastparquet").reset_index(drop=True)
#     hardhat = os.path.join(base, "hardhat")
#     if os.path.exists(os.path.join(hardhat, "contracts")):
#         run(
#             f"""
#             cd {hardhat}
#             rm -rf contracts
#             mkdir contracts
#             """, shell=True
#         )

#     if os.path.exists(os.path.join(hardhat, "artifacts")):
#         run(
#             f"""
#             cd {hardhat}
#             rm -rf artifacts
#             """, shell=True
#         )

#     if os.path.exists(os.path.join(hardhat, "cache")):
#         run(
#             f"""
#             cd {hardhat}
#             rm -rf cache
#             """, shell=True
#         )

#     for i in range(len(test)):
#         source = test.loc[i, "source_code"]
#         with open(os.path.join(hardhat, "contracts", f"sample_{i}.sol"), "w") as f:
#             f.write(source)

#     # Manually
#     for num in [
#         10471,
#         10552,
#         11668,
#         11729,
#         11884,
#         1857,
#         2106,
#         3165,
#         3352,
#         4069,
#         4259,
#         4617,
#         5572,
#         5739,
#         619,
#         6485,
#         6554,
#         6566,
#         6707,
#         7646,
#         8374,
#         8457,
#         8701,
#         9136,
#         9796,
#         9818,
#     ]:
#         run(
#             f"""
#             cd {os.path.join(hardhat, "contracts")}
#             rm sample_{num}.sol
#             """, shell=True
#         )


# def compile(test_source):
#     test = pd.read_parquet(test_source, engine="fastparquet").reset_index(drop=True)
#     pattern = r"contracts/(\w+\.sol)"
#     cnt = 0
#     hardhat = os.path.join(base, "hardhat")
#     while True:
#         cnt += 1
#         print("Loop:", cnt)
#         data = run(
#             f"""
#             cd {hardhat}
#             npx hardhat compile
#             """,
#             shell=True,
#             capture_output=True,
#             text=True,
#         )
#         stdout = data.stdout
#         if stdout != "\n":
#             break
#         stderr = data.stderr
#         print(
#             "-----------------------------------------\n",
#             stderr,
#             "-----------------------------------------\n",
#         )
#         errs = stderr.split("\n\n")
#         print("Number of errors:", len(errs))
#         loop_err_files = set()
#         for err in errs:
#             for err_type in ERROR:
#                 if err_type in err:
#                     match = re.search(pattern, err)
#                     if match:
#                         err_file = match.group(1)
#                         loop_err_files.add(err_file)
#         if not loop_err_files:
#             break
#         for err_file in loop_err_files:
#             run(
#                 f"""cd {os.path.join(hardhat, "contracts")}
#                 rm {err_file}""",
#                 shell=True,
#             )
#             print("Removed:", err_file)


base = os.path.dirname(os.path.abspath(__file__))

from tqdm import tqdm


def compile(input, hardhat, output):
    print(input, hardhat, output)
    compilable = []
    test_compile = pd.read_parquet(input, engine="fastparquet")
    for i in tqdm(test_compile.index):
        source = test_compile.loc[i, "source_code"]
        with open(os.path.join(base, hardhat, "contracts", "sample.sol"), "w") as f:
            f.write(source)
        cmd = f"""
        cd {os.path.join(base, hardhat)}
        npx hardhat compile
        """
        data = run(cmd, shell=True, capture_output=True, text=True)
        if "Compiled 1 Solidity file successfully" in data.stdout:
            compilable.append([i, test_compile.loc[i, "source_code"]])

    compilable = pd.DataFrame(compilable, columns=["index", "source_code"]).set_index(
        "index"
    )
    compilable.to_parquet(output, engine="fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-hh", "--hardhat", dest="hardhat")
    parser.add_argument("-o", "--output", dest="output")
    args = parser.parse_args()
    compile(args.input, args.hardhat, args.output)
