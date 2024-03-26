for PROJECT in /data/hieuvd/lvdthieu/maven_projects/*
do  
    cd "$PROJECT"
    cd $(ls -d */|head -n 1)
    /home/hieuvd/apache-maven-3.6.3/bin/mvn clean compile
    if [ $? -eq 0 ]
    then 
        echo "${PROJECT}\n" >> /data/hieuvd/lvdthieu/maven_projects/compilable.txt
    else
        echo "${PROJECT}\t$?\n" >> /data/hieuvd/lvdthieu/maven_projects/uncompilable.txt
    fi
done