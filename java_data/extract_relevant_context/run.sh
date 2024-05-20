UPDATE=$1
if [ $UPDATE ]
then 
    cd /var/data/lvdthieu/code-generation/java_data/java-parser 
    mvn compile
fi

python /var/data/lvdthieu/code-generation/java_data/extract_relevant_context/run.py \
    --input /var/data/lvdthieu/temp/retry.parquet \
    --num-batch 10 \
    --parser /var/data/lvdthieu/code-generation/java_data/java-parser \
    --base-dir /var/data/lvdthieu/repos/processed-projects