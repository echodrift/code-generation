#!bin/bash

INPUT=$1
OUTPUT=$2
while read PROJ_PATH
do 
    find ${PROJ_PATH} -name '*.java' -print0 | while IFS= read -r -d '' FILE
    do 
        echo "$FILE" >> $OUTPUT
    done
done < $INPUT
