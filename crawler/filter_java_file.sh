while read PROJ_PATH
do 
    find $PROJ_PATH -name '*.java' -print0 | while IFS= read -r -d '' FILE
    do 
        echo "$FILE" >> /home/hieuvd/lvdthieu/CodeGen/crawler/java_file.txt
    done
done < /home/hieuvd/lvdthieu/CodeGen/crawler/left_proj.txt

# while read PROJECT
# do 
#     echo "${PROJECT/'github.com'/api.github.com/repos}" >> /home/hieuvd/lvdthieu/CodeGen/crawler/all_url_v1.txt
# done < /home/hieuvd/lvdthieu/CodeGen/crawler/all_url.txt
