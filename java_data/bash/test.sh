#!bin/bash
cnt=1
while read JAVA_FILE
do  
    if [ ! -f "${JAVA_FILE%.txt}.json}" ]
    then
        sh /home/hieuvd/lvdthieu/CodeGen/java_data/parser/ast2json/run.sh "$JAVA_FILE" "${JAVA_FILE%.txt}.json}"
        echo "$cnt"
        cnt=$((cnt+1))
    fi 
done < $1