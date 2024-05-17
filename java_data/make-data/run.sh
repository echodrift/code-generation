# Crawl data
python java_data/src/crawl.py --repo-info "$FILE_STORE_REPO_INFO" --dir "$DIR_STORE_ALL_REPO"
# Make data
python java_data/src/make_data.py --input "$DIR_STORE_ALL_REPO" --output "$FILE_STORE_RESULT_DATASET"