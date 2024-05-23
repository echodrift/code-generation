# # Instrument
# java -cp $CLOVER com.atlassian.clover.CloverInstr -i clover.db -s src -d build/instr


# # Compile instrument file
# mvn dependency:copy-dependencies
# javac -cp $CLOVER:'target/dependency/*' -d bin build/instr/**/*.java


# # Compile test file
# javac -cp bin:$JUNIT RegressionTest*.java -d bin


# # Run test 
# # java -cp bin:$CLOVER:$JUNIT org.junit.runner.JUnitCore RegressionTest
# # or
# java -cp bin:$ClOVER:$JUNIT org.junit.runner.JUnitCore RegressionTest0#test01

# # Get report
# java -cp $CLOVER com.atlassian.clover.reporters.json.JSONReporter -i clover.db -o clover_json
# # or
# java -cp $CLOVER com.atlassian.clover.reporters.html.HtmlReporter -i clover.db -o clover_html% 

# Run
python /home/hieuvd/lvdthieu/code-generation/java_data/processors/compile_test_executor/run.py \
    --input /home/hieuvd/lvdthieu/test_baseline_v1.parquet \
    --output /home/hieuvd/lvdthieu/test_baseline_compiled.parquet \
    --col generated_code \
    --base-dir /home/hieuvd/lvdthieu/repos/tmp-projects \
    --tmp-dir /home/hieuvd/lvdthieu/repos/tmp \
    --log-dir /home/hieuvd/lvdthieu/repos/log \
    --mvn /home/hieuvd/apache-maven-3.6.3/bin/mvn