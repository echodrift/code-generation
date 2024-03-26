for PROJECT in /data/hieuvd/lvdthieu/*
do  
    if [ "$PROJECT" != "/data/hieuvd/lvdthieu/maven_projects" ] && [ "$PROJECT" != "/data/hieuvd/lvdthieu/not_maven_projects" ]
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
            cd /data/hieuvd/lvdthieu
            mv "$PROJECT" /data/hieuvd/lvdthieu/maven_projects  
        else
            cd /data/hieuvd/lvdthieu
            mv "$PROJECT" /data/hieuvd/lvdthieu/not_maven_projects  
        fi
    fi
done