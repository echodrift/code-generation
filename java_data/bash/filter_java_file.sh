#!bin/bash

INPUT=$1
OUTPUT=$2
INDENT="    "
echo "{" >> $OUTPUT
while read PROJ_PATH
do 
    echo "\"$PROJ_PATH\": [" >> $OUTPUT
    find ${PROJ_PATH} -name '*.java' -print0 | while IFS= read -r -d '' FILE
    do 
        echo "${INDENT}\"${FILE}\"," >> $OUTPUT
    done
    echo "]," >> $OUTPUT
done < $INPUT
echo "}" >> $OUTPUT