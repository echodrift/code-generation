DIR="$( cd "$( dirname "$0" )" && pwd )"
FUNC=$1
INPUT=$2
CONCURRENCY=$3
OUTPUT=$4

############################################################################################################

python $DIR/../tools/sharding.py --input $INPUT --concurrency $CONCURRENCY --output $DIR/data
echo Sharding done
i=1
while [ $i -le $CONCURRENCY ]; do
    screen -dmS parser$i bash -c "node $FUNC -i $DIR/data/batch$i.parquet -o $DIR/out/result$i.parquet"
    i=$(( i + 1 ))
done

############################################################################################################

python $DIR/../tools/merging.py --input $DIR/out --concurrency $CONCURRENCY --output $OUTPUT
echo Merging done
