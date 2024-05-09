OPTION=$1
if (( $OPTION == 1 ))
then
python /var/data/lvdthieu/code-generation/java_data/test_generator/run.py \
        --input /var/data/lvdthieu/temp/almost-final-java.parquet \
        --base-dir /var/data/lvdthieu/repos/processed-projects \
        --time-limit 20 \
        --output-limit 100
elif (( $OPTION == 2 ))
then 
python /var/data/lvdthieu/code-generation/java_data/test_generator/utils.py \
        --task config-maven \
        --input /var/data/lvdthieu/temp/almost-final-java.parquet \
        --base-dir /var/data/lvdthieu/repos/processed-projects

elif (( $OPTION == 3 ))
then
python /var/data/lvdthieu/code-generation/java_data/test_generator/utils.py \
        --task extract-method-qualified-name \
        --input /var/data/lvdthieu/temp/almost-final-java.parquet \
        --num-batch 30 \
        --base-dir /var/data/lvdthieu/repos/processed-projects \
        --parser /var/data/lvdthieu/code-generation/java_data/java-parser
else 
echo "No command"
fi
