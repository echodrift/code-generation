UPDATE=$1
if [ $UPDATE ]
then 
    cd /var/data/lvdthieu/code-generation/java_data/java-parser
    mvn compile
fi

python /var/data/lvdthieu/code-generation/java_data/extract_relevant_context/run.py \
    --input /var/data/lvdthieu/java_filtered.parquet \
    --num-batch 30 \
    --parser /var/data/lvdthieu/code-generation/java_data/java-parser \
    --base-dir /var/data/lvdthieu/repos/processed-projects