UPDATE=$1
if [ $UPDATE ]
then 
    cd /var/data/lvdthieu/code-generation/java_data/extract_relevant_context/java-parser
    mvn compile
fi

python /var/data/lvdthieu/code-generation/java_data/extract_relevant_context/run.py \
    --input /var/data/lvdthieu/new-java.parquet \
    --num-batch 30 \
    --ds /var/data/lvdthieu/code-generation/java_data/extract_relevant_context/data \
    --os /var/data/lvdthieu/code-generation/java_data/extract_relevant_context/out