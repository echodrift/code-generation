cd /var/data/lvdthieu/code-generation/java_data/java-parser
mvn clean compile
cd /var/data/lvdthieu/code-generation/java_data/java-parser/target/classes
java -cp .:/var/data/.m2/org/apache/commons/commons-csv/1.11.0/commons-csv-1.11.0.jar:/var/data/.m2/commons-io/commons-io/2.16.1/commons-io-2.16.1.jar:/var/data/.m2/commons-codec/commons-codec/1.16.1/commons-codec-1.16.1.jar:/var/data/lvdthieu/code-generation/java_data/java-parser/src/main/resources/Flute.jar:/var/data/.m2/me/tongfei/progressbar/0.10.0/progressbar-0.10.0.jar:/var/data/.m2/org/jline/jline/3.23.0/jline-3.23.0.jar \
        Main \
        /var/data/lvdthieu/minitest.csv \
        /var/data/lvdthieu/repos/processed-projects \
        /var/data/lvdthieu/new-java-context.csv
