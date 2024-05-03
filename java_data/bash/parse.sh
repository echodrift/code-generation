#!bin/bash
PARSER="/var/data/lvdthieu/code-generation/java_data/parser"
PROJ_NAMES="/var/data/lvdthieu/projects_name.txt"
DATA_INP="/var/data/lvdthieu/code-generation/java_data/data/projects"
DATA_OUT="/var/data/lvdthieu/code-generation/java_data/data/parsed"

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
    # echo $command
    screen -dmS ${PROJ_NAME} bash -c "$command"
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

