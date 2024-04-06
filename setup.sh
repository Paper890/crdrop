#!/bin/bash

echo -e "ISI TOKEN GITHUB UNTUK REGIS IP"
read -p "Masukkan Token DO :" token_do
read -p "Masukkan Token Telegram : " token_tele
read -p "Masukkan Token Github : " token_git
# Update paket repository
sudo apt update -y

# Upgrade paket yang sudah terinstal
sudo apt upgrade -y

# Instal Python 3 dan pip
sudo apt install python3 python3-pip -y

# Instal dependensi Python
pip install requests
pip install python-telegram-bot==12.0.0
pip install schedule

mkdir -p san/script/bot
# Pindah ke dalam folder yang baru dibuat
cd san/script/bot
# Mengunduh skrip Python
wget https://raw.githubusercontent.com/Paper890/crdrop/main/Do.py
wget https://raw.githubusercontent.com/Paper890/crdrop/main/regis.py

# FOR DO CREATE
TOKEN_DO="$token_do"
sed -i "s/{TOKEN_DO}/$TOKEN_DO/g" Do.py
TOKEN_TELEGRAM="$token_tele"
sed -i "s/{TOKEN_TELEGRAM}/$TOKEN_TELEGRAM/g" Do.py

# FOR REGIS IP
TOKEN_GITHUB="$token_git"
sed -i "s/{TOKEN_DO}/$TOKEN_DO/g" Do.py
TOKEN_TELEGRAM="$token_tele"
sed -i "s/{TOKEN_TELEGRAM}/$TOKEN_TELEGRAM/g" Do.py

# fungsi running as system
cd
cd /etc/systemd/system
wget https://raw.githubusercontent.com/Paper890/crdrop/main/Do.service
sudo systemctl daemon-reload
sudo systemctl start Do
sudo systemctl enable Do
sudo systemctl restart Do

wget https://raw.githubusercontent.com/Paper890/crdrop/main/regis.service
sudo systemctl daemon-reload
sudo systemctl start regis
sudo systemctl enable regis
sudo systemctl restart regis

echo "Instalasi selesai."
