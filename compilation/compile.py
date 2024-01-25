import pandas as pd
from subprocess import run
import argparse
import os
from tqdm import tqdm

base = os.path.dirname(os.path.abspath(__file__))
compiler = os.path.join(base, "compilers")


def compile(
    input: str,
    hardhat: str,
    output: str,
    throw_error: bool = False,
    error_path: str = "",
):
    compilable = []
    if throw_error:
        uncompilable = {}
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
        else:
            if throw_error:
                uncompilable[i] = data.stderr

    compilable = test_compile[test_compile.index.isin(compilable)]
    compilable.to_parquet(output, engine="fastparquet")

    if throw_error:
        error = test_compile[test_compile.index.isin(uncompilable)]
        error["error"] = error.index.apply(lambda i: uncompilable[i])
        uncompilable.to_parquet(error_path, engine="fastparquet")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input")
    parser.add_argument("-hh", "--hardhat", dest="hardhat")
    parser.add_argument("-o", "--output", dest="output")
    parser.add_argument("-e", "--error", dest="error")
    parser.add_argument("-p", "--path", dest="path")
    args = parser.parse_args()
    if args.error == "yes":
        compile(
            input=args.input,
            hardhat=args.hardhat,
            output=args.output,
            throw_error=True,
            error_path=args.path,
        )
    else:
        compile(input=args.input, hardhat=args.hardhat, output=args.output)
