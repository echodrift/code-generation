#!/bin/bash
# Setup
DIR="$( cd "$( dirname "$0" )" && pwd )"
compiler="$DIR/compilers"
input=$1
concurency=$2
output=$3

############################################################################################################

# Compile 

echo "Get error?  (yes/no)"
read get_error
i=1
while [ $i -le $concurency ]; do
    if [ ! -d "$compiler/hardhat$i" ]; then
        cp -r $compiler/hardhat $compiler/hardhat$i
        echo Copied to $compiler/hardhat$i
    else
        if [ -d "$compiler/hardhat$i/artifacts" ]; then
            rm -r $compiler/hardhat$i/artifacts
        fi
        if [ -d "$compiler/hardhat$i/cache" ]; then
            rm -r $compiler/hardhat$i/cache
        fi
    fi
    i=$((i + 1))
done
echo Create folder done
python $DIR/../tools/sharding.py --input $input --concurency $concurency --output $DIR/data
echo Sharding done
i=1
while [ $i -le $concurency ]; do
    screen -dmS hardhat$i bash -c "python compile.py -i $DIR/data/batch$i.parquet -hh hardhat$i -o $DIR/out/result$i.parquet -e $get_error -p $DIR/error/error$i.parquet"
    i=$(( i + 1))
done

############################################################################################################

# Merge output

# python $DIR/../tools/merging.py --input $DIR/out --concurency $concurency --output $output 
# echo Merging done