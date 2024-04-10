#!bin/bash
FLUTE=$1
JAVA_FILES_DIR=$2
CLASS_FILE_DIR=$3
PROJ_NAMES=$4
DATA=$5
while read PROJ_NAME
do  
    echo "$PROJ_NAME"
    command=""
    command+="mkdir -p $CLASS_FILE_DIR/$PROJ_NAME && "
    command+="javac -d $CLASS_FILE_DIR/$PROJ_NAME -cp $FLUTE "
    command+="$JAVA_FILES_DIR/*.java "
    command+="&& cd $CLASS_FILE_DIR/$PROJ_NAME "
    command+="&& java -cp ".:$FLUTE" Main "
    command+="$DATA/projects/project_${PROJ_NAME}.json "
    command+="$DATA/parsed/parsed_${PROJ_NAME}.json"
    screen -dmS ${PROJ_NAME} bash -c "$command"
done < $PROJ_NAMES

# PROJ_NAME="vert-x3_vertx-examples"
# command=""
# command+="mkdir -p $CLASS_FILE_DIR/$PROJ_NAME && "
# command+="javac -d $CLASS_FILE_DIR/$PROJ_NAME -cp $FLUTE "
# command+="$JAVA_FILES_DIR/*.java "
# command+="&& cd $CLASS_FILE_DIR/$PROJ_NAME "
# command+="&& java -cp ".:$FLUTE" Main "
# command+="$DATA/projects/project_${PROJ_NAME}.json "
# command+="$DATA/parsed/parsed_${PROJ_NAME}.json"
# screen -dmS ${PROJ_NAME} bash -c "$command"

