conda -v
if [ $? -eq 0 ]
then
    conda create -n 
else
    python3 -v
    if [ $? -ne 0 ]
    then
        echo "You need to install python3 first"
    fi
fi