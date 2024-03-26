#!bin/bash
# while [ 
# do
#     mkdir /data/hieuvd/lvdthieu
#     xargs --replace -P10 git clone --depth 1 {} < /home/hieuvd/lvdthieu/Crawler/repos.txt
# done

# while IFS=';' read -ra PROJECT
# do 
#     mkdir "/data/hieuvd/lvdthieu/${PROJECT[1]}_${PROJECT[2]}"
#     mv "/data/hieuvd/lvdthieu/${PROJECT[2]}" /data/hieuvd/lvdthieu/${PROJECT[1]}_${PROJECT[2]}
# done < /home/hieuvd/lvdthieu/Crawler/unique_repos.txt

# while [ $(ls /data/hieuvd/lvdthieu | wc -l) -lt 1002 ] 
# do  
    while IFS=';' read -ra PROJECT
    do 
        if [ ! -d "/data/hieuvd/lvdthieu/${PROJECT[1]}_${PROJECT[2]}" ]
        then
            mkdir "/data/hieuvd/lvdthieu/${PROJECT[1]}_${PROJECT[2]}"
            cd "/data/hieuvd/lvdthieu/${PROJECT[1]}_${PROJECT[2]}"
            git clone --depth 1 "${PROJECT[0]}"
            # if [ "$?" -ne 0 ]
            # then 
            #     rm -r "/data/hieuvd/lvdthieu/${PROJECT[1]}_${PROJECT[2]}"
            # fi
        fi
    done < /home/hieuvd/lvdthieu/Crawler/not_unique_repos.txt
# done 