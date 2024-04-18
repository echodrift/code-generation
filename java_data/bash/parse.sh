#!bin/bash
PARSER=$1
PROJ_NAMES=$2
DATA_INP=$3 
DATA_OUT=$4
while read PROJ_NAME
do  
    command=""
    command+="mkdir -p $PARSER/classes/$PROJ_NAME && "
    command+="javac -d $PARSER/classes/$PROJ_NAME -cp "$PARSER/lib/Flute.jar" "
    command+="$PARSER/src/*.java "
    command+="&& cd $PARSER/classes/$PROJ_NAME "
    command+="&& java -cp ".:$PARSER/lib/Flute.jar" Main "
    command+="${DATA_INP}/project_${PROJ_NAME}.json "
    command+="${DATA_OUT}/parsed_${PROJ_NAME}.json"
    echo $command
    # screen -dmS ${PROJ_NAME} bash -c "$command"
    if [ $? -eq 0 ]
    then
        echo "Make a screen for $PROJ_NAME"
    else
        echo "Error"
    fi
done < $PROJ_NAMES

# PROJ_NAME="brettwooldridge_HikariCP"
# echo "$PROJ_NAME"
# command=""
# command+="mkdir -p $PARSER/classes/$PROJ_NAME && "
# command+="javac -d $PARSER/classes/$PROJ_NAME -cp "$PARSER/lib/Flute.jar" "
# command+="$PARSER/src/*.java "
# command+="&& cd $PARSER/classes/$PROJ_NAME "
# command+="&& java -cp ".:$PARSER/lib/Flute.jar" Main "
# command+="${DATA_INP}/project_${PROJ_NAME}.json "
# command+="${DATA_OUT}/parsed_${PROJ_NAME}.json"
# eval "$command"

