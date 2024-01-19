#!/bin/bash
DIR="$( cd "$( dirname "$0" )" && pwd )"
file_source=$1
concurency=$2
output_dir=$3
for (( i=1; i <= $concurency; i++ ))
do
    if [ ! -d $DIR/hardhat$i ]; then
        cp -r $DIR/hardhat $DIR/hardhat$i
        echo Copied to $DIR/hardhat$i
    fi
done
echo Create folder done
python initial.py --path $file_source --concurency $concurency
echo Initial done
for (( i=1; i <= $concurency; i++ ))
do
    echo "conda activate codegen; python compile.py -p $DIR/../data/compile/batch$i.parquet -hh hardhat$i -o $output_dir/result$i.parquet;" > test
    screen -dmS hardhat$i bash test
done