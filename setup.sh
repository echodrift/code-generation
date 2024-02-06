which conda
if [ $? -eq 0 ]
then
    conda create -n gen python=3.11
    pip install -r requirements.txt
    conda activate gen
else
    which python3
    if [ $? -ne 0 ]
    then
        echo "You need to install python3"
        exit 1
    else
        pip install -r requirements.txt
    fi
fi

which node
if [ $? -ne 0 ]
then 
    echo "You need to install node"
    exit 1
fi


cd parser
npm install
cd ../solium
npm install
cd ../compilation/compilers/hardhat
npm install

