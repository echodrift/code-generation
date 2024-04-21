#!/bin/bash
PROJECT_STORAGE_DIR=$1  
MVN=$2  
COMPILABLE=$3  
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