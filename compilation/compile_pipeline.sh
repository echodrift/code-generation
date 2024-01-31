#!/bin/bash
DIR=$(realpath $(dirname $0))
COMPILE_INFO="/home/hieuvd/lvdthieu/CodeGen/data/compile_info"
COMPILER="$DIR/compilers"
INPUT=$1
RESULT_FOLDER=$2
CONCURRENCY=$3
PHASE=$4
INPUT_DIR=$(realpath $(dirname $1))

if [ "$PHASE" = "compile" ]
then
python $DIR/../tools/funcs.py --func raw_test --input $INPUT --output $INPUT_DIR/raw_test.parquet
echo "Make raw test done"
python $DIR/../tools/funcs.py --func test_suite --input $INPUT_DIR/raw_test.parquet --output $INPUT_DIR/test_suite.parquet
echo "Make test suite done"
python $DIR/../tools/funcs.py --func split_test_suite --input $INPUT_DIR/test_suite.parquet --output $INPUT_DIR
echo "Split test suite done"

i=1
while [ $i -le $CONCURRENCY ]; do
    if [ ! -d "$COMPILER/hardhat$i" ]; then
        cp -r $COMPILER/hardhat $COMPILER/hardhat$i
        echo "Copied to $COMPILER/hardhat$i"
    else
        if [ -d "$COMPILER/hardhat$i/artifacts" ]
        then
            rm -rf $COMPILER/hardhat$i/artifacts
            echo "Removed hardhat$i artifacts"
        fi
        if [ -d "$COMPILER/hardhat$i/cache" ]
        then
            rm -rf $COMPILER/hardhat$i/cache
            echo "Removed hardhat$i cache"
        fi
    fi
    i=$((i + 1))
    
done
echo "Create folder done"

python $DIR/../tools/funcs.py --func sharding --input $INPUT_DIR/deepseek.parquet --concurrency $CONCURRENCY --output $DIR/data
echo "Sharding done"

i=1

while [ $i -le $CONCURRENCY ]; do
    screen -dmS hardhat$i bash -c "python compile.py -i $DIR/data/batch$i.parquet -hh hardhat$i -o $DIR/out/result$i.parquet"
    i=$(( i + 1))
done

else
# Merging
if [ ! -d $COMPILE_INFO/$RESULT_FOLDER ]
then
    mkdir $COMPILE_INFO/$RESULT_FOLDER
fi

python $DIR/../tools/funcs.py --func merging --input $DIR/out --concurrency $CONCURRENCY --output $COMPILE_INFO/$RESULT_FOLDER/deepseek.parquet 
echo Merging done
fi



