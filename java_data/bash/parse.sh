while read PROJ_NAME
do
    command=""
    command+="mkdir $(pwd)/$PROJ_NAME && "
    command+="javac -d $(pwd)/$PROJ_NAME -cp /home/hieuvd/lvdthieu/CodeGen/java_data/parser/lib/Flute.jar "
    command+="/home/hieuvd/lvdthieu/CodeGen/java_data/parser/src/Main.java "
    command+="/home/hieuvd/lvdthieu/CodeGen/java_data/parser/src/Project.java "
    command+="/home/hieuvd/lvdthieu/CodeGen/java_data/parser/src/ClassInfo.java "
    command+="&& cd $(pwd)/$PROJ_NAME "
    command+="&& java -cp .:/home/hieuvd/lvdthieu/CodeGen/java_data/parser/lib/Flute.jar Main "
    command+="/home/hieuvd/lvdthieu/CodeGen/java_data/data/java-36k/project_${PROJ_NAME}.json "
    command+="/home/hieuvd/lvdthieu/CodeGen/java_data/data/java-36k/parse_${PROJ_NAME}.json"
    screen -dmS ${PROJ_NAME} bash -c "$command"
done < /home/hieuvd/lvdthieu/CodeGen/java_data/data/urls/projects.txt
# PROJ_NAME="AdoptOpenJDK_jitwatch"

# eval $command