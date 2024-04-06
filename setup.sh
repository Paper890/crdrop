#!/bin/bash

sudo apt update -y
sudo apt upgrade -y
sudo apt install python3 python3-pip -y
apt install python3-pip -y
pip install requests
pip install python-telegram-bot==12.0.0
pip install schedule

mkdir -p san/bot
cd
cd san/bot
git clone https://github.com/Paper890/crdrop.git
touch tokens.txt
