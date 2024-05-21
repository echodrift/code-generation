# Instrument
java -cp $CLOVER com.atlassian.clover.CloverInstr -i clover.db -s src -d build/instr


# Compile instrument file
mvn dependency:copy-dependencies
javac -cp $CLOVER:'target/dependency/*' -d bin build/instr/**/*.java


# Compile test file
javac -cp bin:$JUNIT RegressionTest*.java -d bin


# Run test 
# java -cp bin:$CLOVER:$JUNIT org.junit.runner.JUnitCore RegressionTest
# or
java -cp bin:$ClOVER:$JUNIT org.junit.runner.JUnitCore RegressionTest0#test01

# Get report
java -cp $CLOVER com.atlassian.clover.reporters.json.JSONReporter -i clover.db -o clover_json
# or
java -cp $CLOVER com.atlassian.clover.reporters.html.HtmlReporter -i clover.db -o clover_html% 

# Run
python /var/data/lvdthieu/code-generation/java_data/processors/compile_test_executor/run.py --input /var/data/lvdthieu/new_test.parquet --output /var/data/lvdthieu/test_executor.parquet --col generated_col --base-dir /var/data/lvdthieu/repos/tmp --tmp-dir /var/data/lvdthieu/repos/tmp1 --mvn /var/data/lvdthieu/apache-maven-3.6.3/bin/mvn