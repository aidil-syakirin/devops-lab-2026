#!/bin/bash

echo "updating VM"
sudo apt update
echo "VM update done"

cd ~/flask-app

git pull origin main

echo "bringing docker images down"
docker compose down -v

echo "building docker images in progress"
docker compose build --no-cache

echo "bring docker images up"
docker compose up -d

echo "docker images already up and running"

