#!/bin/bash
DIR="$( cd "$( dirname "$0" )" && pwd )"
input=$1
concurency=$2
output=$3

############################################################################################################

# i=1
# while [ $i -le $concurency ]; do
#     if [ ! -d "$DIR/hardhat$i" ]; then
#         cp -r $DIR/hardhat $DIR/hardhat$i
#         echo Copied to $DIR/hardhat$i
#     else
#         if [ -d "$DIR/hardhat$i/artifacts" ]; then
#             rm -r $DIR/hardhat$i/artifacts
#         fi
#         if [ -d "$DIR/hardhat$i/cache" ]; then
#             rm -r $DIR/hardhat$i/cache
#         fi
#     fi
#     i=$((i + 1))
# done
# echo Create folder done
# python sharding.py --input $input --concurency $concurency --output $DIR/data
# echo Sharding done
# i=1
# while [ $i -le $concurency ]; do
#     screen -dmS hardhat$i bash -c "python compile.py -i $DIR/data/batch$i.parquet -hh hardhat$i -o $DIR/out/result$i.parquet"
#     i=$(( i + 1))
# done

############################################################################################################

python merging.py --input $DIR/out --concurency $concurency --output $output 
echo Merging done
