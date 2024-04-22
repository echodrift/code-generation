from java.java8.JavaLexer import JavaLexer
from antlr4 import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def count_java_tokens_antlr4(code):
    lexer = JavaLexer(InputStream(code))
    token_count = 0
    for token in lexer.getAllTokens():
        token_count += 1
    return token_count


def cr_and_num_token(dataset_url: str, compile_info_col: str):
    
    df = pd.read_parquet(dataset_url, "fastparquet")
    df["len_func_body"] = df["func_body"].apply(lambda func: count_java_tokens_antlr4(func))
    print(df["len_func_body"].describe())
    from collections import defaultdict
    buckets = [(3, 10), (10, 33), (33, 50), (50, 102), (102, 200), (200, 400), (400, 800), (800, 1300)]
    stats = {}
    for _, row in df.iterrows():
        for bucket in buckets:
            if row["len_func_body"] >= bucket[0] and row["len_func_body"] < bucket[1]:
                tmp = stats.get(bucket, [0, 0])
                tmp[0] += 1
                if row[compile_info_col] == "<COMPILED_SUCCESSFULLY>":
                    tmp[1] += 1
                stats[bucket] = tmp
                break
    # Data
    intervals = [str(bucket) for bucket in buckets]
    compilables = [stats[bucket][1] for bucket in buckets]
    totals = [stats[bucket][0] for bucket in buckets]
    percentages = [stats[bucket][1] / stats[bucket][0] * 100 for bucket in buckets]
    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    bar_width = 0.35
    x = np.arange(len(intervals))

    bars1 = ax1.bar(x - bar_width/2, compilables, bar_width, color='skyblue', label='#Compilable')
    bars2 = ax1.bar(x + bar_width/2, totals, bar_width, color='orange', label='#Func')
    # Add percentages above each column
    for bar, compilable in zip(bars1, compilables):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, compilable, ha='center')

    # Add values above each column in the additional column
    for bar, value in zip(bars2, totals):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, value, ha='center', color='black')
    
    ax2.plot(x, percentages, marker='o', color='blue', label='Percentage', linestyle='-')
    for i, percentage in enumerate(percentages):
        ax2.text(i, percentage, f'{percentage:.2f}%', ha='right', va='bottom')
        
    ax1.set_xlabel('Function Body Length')
    ax1.set_ylabel('Compilable / Num_Func')
    ax2.set_ylabel('Percentage')
    plt.title('Distribution')
    ax1.set_xticks(x, intervals, rotation=45, ha='right')
    ax1.legend(loc="center right")
    ax1.set_ylim(0, max(max(compilables), max(totals)) + 100)
    ax2.set_ylim(0, 100)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def check_compilable_rate(dataset_url: str, compile_info_col: str="compile_info_filled_file_baseline_output") -> int:
    import pandas as pd
    df = pd.read_parquet(dataset_url, "fastparquet")
    return len(df[df[compile_info_col] == "<COMPILED_SUCCESSFULLY>"]) / len(df)


def jsonl2parquet(src: str, dst: str):
    import pandas as pd
    df = pd.read_json(src, lines=True)
    print(df.info())
    df.to_parquet(dst, "fastparquet")


from extract_parent_context import extract_signature_and_var

java_code = """
public class Test {
    public static void main(String[] args) {
        int a = 10;
        int b = 20;
        int c = a + b;
    }
}

public class Test2 {
    public static void main(String[] args) {
        int a = 10;
        int b = 20;
        int c = a + b;
    }
}
"""

print(extract_signature_and_var(java_code))