- Run crawl.py
```bash
python java_data/src/crawl.py --repo-info "$FILE_STORE_REPO_INFO" --dir "$DIR_STORE_ALL_REPO"
```

- Run fill_code.py
```bash
python java_data/src/fill_code.py --input "$FILE_STORE_INPUT_DATASET" --input-type "$INPUT_FILE_TYPE" --col "$GENERATED_CODE_COLUMN" --dir "$DIR_STORE_ALL_REPO" --output "$FILE_STORE_RESULT_DATASET"
```

- Run make_data.py
```bash
python java_data/src/make_data.py --input "$DIR_STORE_ALL_REPO" --output "$FILE_STORE_RESULT_DATASET"
```




- Get compiler feedback

```bash
python java_data/src/fill_code.py --input /var/data/lvdthieu/code-generation/java_data/data/data/starcoder-java-refinerefine.jsonl -o /var/data/lvdthieu/code-generation/java_data/data/data/starcoder-java-refinerefine.parquet -c finetune_output -d /var/data/lvdthieu/repos/processed-projects -t jsonl

python java_data/src/get_compilable_feedback.py --input /var/data/lvdthieu/code-generation/java_data/data/data/deepseek-baseline-java.jsonl --output /var/data/lvdthieu/code-generation/java_data/data/data/deepseek-baseline-java-cr.parquet --dir /var/data/lvdthieu/repos/processed-projects --tmp /var/data/lvdthieu/tmp --col deepseek_baseline_output --mvn /var/data/lvdthieu/apache-maven-3.6.3/bin/mvn --type jsonl
```