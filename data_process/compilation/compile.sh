#!/bin/bash
DIR=$(realpath $(dirname $0))
COMPILER="$DIR/compilers"
INPUT=$1
OUTPUT=$2
CONCURRENCY=$3
PHASE=$4
INPUT_DIR=$(realpath $(dirname $1))

if [ "$PHASE" = "compile" ] 
then
    python "$DIR/../tools/funcs.py" --func raw_test --input "$INPUT" --output "$INPUT_DIR/raw_test.parquet"
    if [ $? -ne 0 ]
    then 
        exit 1
    fi
    echo "Make raw test done"
    python "$DIR/../tools/funcs.py" --func test_suite --input "$INPUT_DIR/raw_test.parquet" --output "$INPUT_DIR/test_suite.parquet"
    if [ $? -ne 0]
    then 
        exit 2
    fi
    echo "Make test suite done"
    i=1
    while [ $i -le $CONCURRENCY ]; do
        if [ ! -d "$COMPILER/hardhat$i" ]; then
            cp -r "$COMPILER/hardhat $COMPILER/hardhat$i"
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
    python "$DIR/../tools/funcs.py" --func sharding --input "$INPUT_DIR/test_suite.parquet" --concurrency $CONCURRENCY --output "$DIR/data"
    if [ $? -ne 0 ]
    then    
        exit 4
    fi
    echo "Sharding done"
    i=1
    while [ $i -le $CONCURRENCY ]; do
        screen -dmS hardhat$i bash -c "python compile.py -i $DIR/data/batch$i.parquet -hh hardhat$i -o $DIR/out/result$i.parquet"
        i=$(( i + 1))
    done
else 
    if [ "$PHASE" = "merge" ] 
    then
        if [ ! -d $OUTPUT ]
        then
            mkdir $OUTPUT
        fi

        python "$DIR/../tools/funcs.py" --func merging --input "$DIR/out" --concurrency $CONCURRENCY --output "$OUTPUT/result.parquet" 
        if [ $? -ne 0 ]
        then
            exit 5
        fi
        echo "Merging done"
        # python "$DIR/../tools/funcs.py" --func extract_error --input "$OUTPUT/result.parquet" --output "$COMPILE_INFO/$RESULT_FOLDER/deepseek_compile_error.parquet
        # echo "Extract errors done"
    else
        if [ "$PHASE" == "cr" ]
        then
            python $DIR/../tools/funcs.py --func cr --input "$OUTPUT/result.parquet"
            if [ $? -ne 0 ]
            then
                exit 6
            fi
        else
            exit 0
        fi
    fi
fi