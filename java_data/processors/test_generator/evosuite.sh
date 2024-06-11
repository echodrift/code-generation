python /home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/evosuite.py \
    --input /home/hieuvd/lvdthieu/admin.parquet \
    --output /home/hieuvd/lvdthieu/admin_evosuite.parquet \
    --base-dir /data/hieuvd/lvdthieu/repos/tmp-projects \
    --time-limit 30 \
    --evosuite /home/hieuvd/lvdthieu/code-generation/java_data/processors/test_generator/lib/evosuite-1.0.6.jar \
    --output-dir /data/hieuvd/lvdthieu/repos/evosuite \
    --log-dir /home/hieuvd/lvdthieu/log_admin_classgraph \
    --proc 1
