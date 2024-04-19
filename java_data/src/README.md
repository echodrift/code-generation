- Get compiler feedback

```bash
python java_data/src/fill_code.py --input /var/data/lvdthieu/code-generation/java_data/data/data/starcoder-java-refinerefine.jsonl -o /var/data/lvdthieu/code-generation/java_data/data/data/starcoder-java-refinerefine.parquet -c finetune_output -d /var/data/lvdthieu/repos/processed-projects -t jsonl

python java_data/src/get_compilable_feedback.py --input /var/data/lvdthieu/code-generation/java_data/data/data/deepseek-baseline-java.jsonl --output /var/data/lvdthieu/code-generation/java_data/data/data/deepseek-baseline-java-cr.parquet --dir /var/data/lvdthieu/repos/processed-projects --tmp /var/data/lvdthieu/tmp --col deepseek_baseline_output --mvn /var/data/lvdthieu/apache-maven-3.6.3/bin/mvn --type jsonl
```