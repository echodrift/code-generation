DIR="$( cd "$( dirname "$0" )" && pwd )"
func=$1
input=$2
concurency=$3
output=$4

############################################################################################################

# python $DIR/../tools/sharding.py --input $input --concurency $concurency --output $DIR/data
# echo Sharding done
# i=1
# while [ $i -le $concurency ]; do
#     screen -dmS parser$i bash -c "node $func -i $DIR/data/batch$i.parquet -o $DIR/out/result$i.parquet"
#     i=$(( i + 1))
# done

############################################################################################################

python $DIR/../tools/merging.py --input $DIR/out --concurency $concurency --output $output 
echo Merging done
