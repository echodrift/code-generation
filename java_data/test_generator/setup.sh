BASEDIR=$(dirname $0)
export RANDOOP=$BASEDIR/lib/randoop-4.3.3/randoop-all-4.3.3.jar
export JUNIT=$BASEDIR/lib/hamcrest-core-1.3.jar:$(pwd)/lib/junit-4.12.jar
export gentest="java -classpath .:target/classes:$RANDOOP randoop.main.Main gentests"
alias compile_test="javac -classpath .:target/classes:$JUNIT RegressionTest*.java"
alias run_test="java -classpath .:target/classes:$JUNIT:. org.junit.runner.JUnitCore RegressionTest"