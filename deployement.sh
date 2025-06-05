#!/bin/bash


cloning_repo()
{


	echo "clonning repo....."


	git clone https://github.com/TanmayAT/AI-Agent-Scratch2Dev.git


	echo "cloning done"



}


install_requirements() {
    echo "Installing dependencies..."
    sudo apt-get update && sudo apt-get install -y docker.io nginx docker-compose || {
        echo "Failed to install dependencies."
        return 1
    }
}


deploy() {
    echo "Building and deploying the Django app..."
    docker compose build . && docker-compose up -d || {
        echo "Failed to build and deploy the app."
        return 1
    }
}




#function calling :  



echo "caling fucntions"


cloning_repo

install_requiments

cd /AI-Agent-Scratch2Dev


cd src

python.exe -m pip install requirements.txt

cd ../

deploy 



