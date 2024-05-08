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
        --input /var/data/lvdthieu/temp/almost-final-java.parquet \
        --base-dir /var/data/lvdthieu/repos/processed-projects
else 
echo "No command"
fi
