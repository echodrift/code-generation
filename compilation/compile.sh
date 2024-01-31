#!/bin/bash
# Setup
DIR="$( cd "$( dirname "$0" )" && pwd )"
COMPILER="$DIR/compilers"
TMP="$DIR/tmp"
INPUT=$1
CONCURRENCY=$2
OUTPUT=$3
COMPILE_INFO=$4

############################################################################################################

# Compile 

# i=1
# while [ $i -le $CONCURRENCY ]; do
#     if [ ! -d "$COMPILER/hardhat$i" ]; then
#         cp -r $COMPILER/hardhat $COMPILER/hardhat$i
#         echo Copied to $COMPILER/hardhat$i
#     else
#         if [ -d "$COMPILER/hardhat$i/artifacts" ]; then
#             rm -r $COMPILER/hardhat$i/artifacts
#         fi
#         if [ -d "$COMPILER/hardhat$i/cache" ]; then
#             rm -r $COMPILER/hardhat$i/cache
#         fi
#     fi
#     i=$((i + 1))
# done
# echo Create folder done
# python $DIR/../tools/funcs.py --func sharding --input $INPUT --concurrency $CONCURRENCY --output $DIR/data
# echo Sharding done

# i=1

# while [ $i -le $CONCURRENCY ]; do
#     screen -dmS hardhat$i bash -c "python compile.py -i $DIR/data/batch$i.parquet -hh hardhat$i -o $DIR/out/result$i.parquet -e $DIR/error/result$i.parquet"
#     i=$(( i + 1))
# done

############################################################################################################

# Merging

python $DIR/../tools/funcs.py --func merging --input $DIR/out --concurrency $CONCURRENCY --output $OUTPUT 
python $DIR/../tools/funcs.py --func merging --input $DIR/error --concurrency $CONCURRENCY --output $COMPILE_INFO
echo Merging done