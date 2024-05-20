UPDATE=$1
if [ $UPDATE ]
then 
    cd /home/hieuvd/lvdthieu/CodeGen/java_data/java-parser 
    /home/hieuvd/apache-maven-3.6.3/bin/mvn compile
    /home/hieuvd/apache-maven-3.6.3/bin/mvn dependency:copy-dependencies
fi

python /home/hieuvd/lvdthieu/CodeGen/java_data/extract_relevant_context/run.py \
    --input /home/hieuvd/lvdthieu/checkpoint.parquet \
    --num-batch 100 \
    --parser /home/hieuvd/lvdthieu/CodeGen/java_data/java-parser \
    --base-dir /home/hieuvd/lvdthieu/repos/processed-projects