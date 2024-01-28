import pandas as pd
from subprocess import run
import argparse
import os
from tqdm import tqdm

base = os.path.dirname(os.path.abspath(__file__))
compiler = os.path.join(base, "compilers")


def compile(input: str, hardhat: str, output: str, error_path: str):
    """Compile a solidity file

    Args:
        input (str): Parquet file store solidity files path
        hardhat (str): Hardhat compiler path
        output (str): Compile result path
        error_path (str): Compile error file path
    """
    compilable = []
    uncompilable = []
    test_compile = pd.read_parquet(input, engine="fastparquet")
    for i in tqdm(test_compile.index):
        source = test_compile.loc[i, "source_code"]
        with open(os.path.join(compiler, hardhat, "contracts", "sample.sol"), "w") as f:
            f.write(source)
        cmd = f"""
        cd {os.path.join(compiler, hardhat)}
        npx hardhat compile --force
        """
        data = run(cmd, shell=True, capture_output=True, text=True)
        if "Compiled 1 Solidity file successfully" in data.stdout:
            compilable.append(i)
            uncompilable.append("<COMPILED_SUCCESSFULLY>")
        else:
            uncompilable.append(data.stderr)

    compilable = test_compile[test_compile.index.isin(compilable)]
    compilable.to_parquet(output, engine="fastparquet")

    error = test_compile
    error["compile_info"] = uncompilable
    error.to_parquet(error_path, engine="fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-hh", "--hardhat", dest="hardhat")
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-e", "--error", dest="error")
    args = parser.parse_args()
    compile(
        input=args.input,
        hardhat=args.hardhat,
        output=args.output,
        error_path=args.error,
    )
