- Run crawl.py
```bash

```

- Run fill_code.py
```bash
python java_data/src/fill_code.py --input "$FILE_STORE_INPUT_DATASET" --input-type "$INPUT_FILE_TYPE" --col "$GENERATED_CODE_COLUMN" --dir "$DIR_STORE_ALL_REPO" --output "$FILE_STORE_RESULT_DATASET"
```

- Run make_data.py
```bash

```

- Run get_compiler_feedback.py
```bash
python java_data/src/get_compiler_feedback.py --input "$FILE_STORE_INPUT_DATASET" --input-type "$INPUT_FILE_TYPE" --output "$FILE_STORE_RESULT_DATASET" --dir "$DIR_STORE_ALL_REPO" --tmp "$DIR_STORE_TMP_PROJECT" --col "$GENERATED_CODE_COLUMN" --mvn "$MAVEN" --logfile "$FILE_STORE_LOG"
```