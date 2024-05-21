OPTION=$1
if (( $OPTION == 1 ))
then
python /home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/run.py \
        --input /home/hieuvd/lvdthieu/checkpoint.parquet \
        --base-dir /home/hieuvd/lvdthieu/repos/processed-projects \
        --time-limit 20 \
        --output-limit 50 \
        --output /home/hieuvd/lvdthieu/generate_status_0.parquet \
        --randoop /home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/lib/randoop-4.3.3/randoop-all-4.3.3.jar
elif (( $OPTION == 2 ))
then
python /home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/utils/utils.py \
        --task config-maven \
        --input /home/hieuvd/lvdthieu/checkpoint.parquet \
        --base-dir /home/hieuvd/lvdthieu/repos/processed-projects \
        --mvn /home/hieuvd/apache-maven-3.6.3/bin/mvn

elif (( $OPTION == 3 ))
then
python /home/hieuvd/lvdthieu/code-generation/java_data/test_generator/utils.py \
        --task extract-method-qualified-name \
        --input /var/data/lvdthieu/temp/almost-final-java.parquet \
        --num-batch 30 \
        --base-dir /var/data/lvdthieu/repos/processed-projects \
        --parser /var/data/lvdthieu/code-generation/java_data/java-parser
else 
echo "No command"
fi
