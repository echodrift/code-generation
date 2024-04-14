PROJECT_STORAGE_DIR=$1  # /data/hieuvd/lvdthieu
MAVEN_PROJECTS_DIR="$PROJECT_STORAGE_DIR"/maven-projects
NOT_MAVEN_PROJECTS_DIR="$PROJECT_STORAGE_DIR"/not-maven-projects
PROCESSED_PROJECT_DIR="$PROJECT_STORAGE_DIR"/processed-projects

for PROJECT in "$PROJECT_STORAGE_DIR"/*
do  
    if [ -d "$PROJECT" ] && [ "$PROJECT" != "$MAVEN_PROJECTS_DIR" ] \
     && [ "$PROJECT" != "$NOT_MAVEN_PROJECTS_DIR" ] \
     && [ "$PROJECT" != "$PROCESSED_PROJECT_DIR" ]
    then
        cd "$PROJECT"
        cd $(ls -d */|head -n 1)
        if [ "$?" -ne 0 ]
        then
            echo "$PROJECT"
            break
        fi
        if ls | grep "pom.xml"
        then
            mv "$PROJECT" "$MAVEN_PROJECTS_DIR"  
        else
            mv "$PROJECT" "$NOT_MAVEN_PROJECTS_DIR" 
        fi
    fi
done