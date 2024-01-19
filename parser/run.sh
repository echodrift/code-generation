DIR="$( cd "$( dirname "$0" )" && pwd )"
file_source=$1
concurency=$2
output_dir=$3
python sharding.py --path $file_source --concurency $concurency --out $DIR/data
echo Sharding done
for (( i=1; i <= $concurency; i++ ))
do
    echo "conda activate codegen; python compile.py -p $DIR/../data/compile/batch$i.parquet -hh hardhat$i -o $output_dir/result$i.parquet;" > test
    screen -dmS hardhat$i bash test
done