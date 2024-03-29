INPUT=$1
COL=$2
INTER=$3
TMP=$4
OUTPUT=$5

python /home/hieuvd/lvdthieu/CodeGen/java_data/parse.py -f ff -i "$INPUT" --col "$COL" -d "/data/hieuvd/lvdthieu/maven_projects" -o "$INTER" 
echo "Fill file done"
python /home/hieuvd/lvdthieu/CodeGen/java_data/funcs.py -i "$INTER" -d "/data/hieuvd/lvdthieu/maven_projects" -t "$TMP" --col "filled_file_$COL" -o "$OUTPUT"