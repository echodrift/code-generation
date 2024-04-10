#!/bin/bash
PROJECT_STORAGE_DIR=$1  # /data/hieuvd/lvdthieu/maven_projects
MVN=$2  # /home/hieuvd/apache-maven-3.6.3/bin/mvn
COMPILABLE=$3  # /data/hieuvd/lvdthieu/compilable.txt
UNCOMPILABLE=$4  
for PROJECT in "$PROJECT_STORAGE_DIR"/*
do  
    echo "-------------------------------------------------------------------"
    echo "-------------------------------------------------------------------"
    echo "$PROJECT"
    echo "-------------------------------------------------------------------"
    echo "-------------------------------------------------------------------"
    cd "$PROJECT"
    cd $(ls -d */|head -n 1)
    $MVN clean compile
    if [ $? -eq 0 ]
    then 
        echo "${PROJECT}" >> $COMPILABLE
    else
        echo "${PROJECT}" >> $UNCOMPILABLE
    fi
done