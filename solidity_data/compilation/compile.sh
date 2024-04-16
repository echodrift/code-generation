#!/bin/bash
DIR=$(realpath $(dirname $0))
COMPILER="$DIR/compilers"
INPUT=$1
COL=$2
OUTPUT=$3
CONCURRENCY=$4
PHASE=$5

if [ "$PHASE" = "compile" ] 
then
    python "$DIR/../tools/funcs.py" --func raw_test --input "$INPUT" --output "$DIR/tmp/raw_test.parquet"
    if [ $? -ne 0 ]
    then 
        exit 1
    fi
    echo "Make raw test done"
    python "$DIR/../tools/funcs.py" --func test_suite --input "$DIR/tmp/raw_test.parquet" --output "$DIR/tmp/test_suite.parquet" --col $COL
    if [ $? -ne 0 ]
    then 
        exit 2
    fi
    echo "Make test suite done"
    i=1
    while [ $i -le $CONCURRENCY ]; do
        if [ ! -d "$COMPILER/hardhat$i" ]; then
            cp -rf "$COMPILER/hardhat" "$COMPILER/hardhat$i"
            if [ $? -ne 0 ]
            then 
                exit 3
            fi
            echo "Copied to $COMPILER/hardhat$i"
        else
            if [ -d "$COMPILER/hardhat$i/artifacts" ]
            then
                rm -rf "$COMPILER/hardhat$i/artifacts"
                if [ $? -ne 0 ]
                then 
                    exit 3
                fi
                echo "Removed hardhat$i artifacts"
            fi
            if [ -d "$COMPILER/hardhat$i/cache" ]
            then
                rm -rf "$COMPILER/hardhat$i/cache"
                if [ $? -ne 0 ]
                then 
                    exit 3
                fi
                echo "Removed hardhat$i cache"
            fi
        fi
        i=$((i + 1))
    done
    echo "Create folder done"
    python "$DIR/../tools/funcs.py" --func sharding --input "$DIR/tmp/test_suite.parquet" --concurrency $CONCURRENCY --output "$DIR/data"
    if [ $? -ne 0 ]
    then    
        exit 4
    fi
    echo "Sharding done"
    i=1
    while [ $i -le $CONCURRENCY ]; do
        screen -dmS hardhat$i bash -c "python $DIR/compile.py -i $DIR/data/batch$i.parquet -hh hardhat$i -o $DIR/out/result$i.parquet"
        i=$(( i + 1))
    done
else 
    if [ "$PHASE" = "merge" ] 
    then
        python "$DIR/../tools/funcs.py" --func merging --input "$DIR/out" --concurrency $CONCURRENCY --output "$OUTPUT" 
        if [ $? -ne 0 ]
        then
            exit 5
        fi
        echo "Merging done"
    else
        if [ "$PHASE" = "cr" ]
        then
            python $DIR/../tools/funcs.py --func cr --input "$OUTPUT"
            if [ $? -ne 0 ]
            then
                exit 6
            fi
        else
            exit 0
        fi
    fi
fi