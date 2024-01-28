which conda
if [ $? -eq 0 ]
then
    conda create -n gen python=3.11
else
    which python3
    if [ $? -ne 0 ]
    then
        echo "You need to install python3"
        exit 1
    fi
fi

which node
if [ $? -ne 0 ]
then 
    echo "You need to install node"
    exit 1
fi

pip install -r requirements.txt
cd parser
npm install
cd ../solium
npm install
cd ../compilation/compilers/hardhat
npm install

