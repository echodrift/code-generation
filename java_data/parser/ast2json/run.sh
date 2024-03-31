# TODO: javadoc, extendedOperands not implemented - removing from JSON output
# Usage: ./run.sh -c '../../Test.java'
DIR=$(realpath $(dirname -- "$0"))
FILE=$1
javac -Xlint:deprecation -cp "$DIR/lib/*" $DIR/*.java  
cd $DIR
java -Xss4m -cp ".:lib/*" "App" "$FILE" | \
sed '/^[ \t]*javadoc: null,$/d' | sed '/^[ \t]*extendedOperands: \[\]$/d' | \
tee /dev/tty > $2
if [ "$?" -ne 0 ]
then
    "$FILE" >> "/home/hieuvd/lvdthieu/CodeGen/java_data/error.txt"
fi
