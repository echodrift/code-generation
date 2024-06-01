UPDATE=$1
if [ $UPDATE ]
then 
    cd /var/data/lvdthieu/code-generation/java_data/processors/java_parser 
    mvn compile
    mvn dependency:copy-dependencies
fi

python /var/data/lvdthieu/code-generation/java_data/processors/extract_relevant_context/run.py \
    --input /var/data/lvdthieu/checkpoint.parquet \
    --parser /var/data/lvdthieu/code-generation/java_data/processors/java_parser \
    --base-dir /var/data/lvdthieu/repos/processed-projects \
    --output /var/data/lvdthieu/checkpoint_relevent_context.csv \
    --log-dir /var/data/lvdthieu/repos/log