#!/bin/bash

cd
rm -r san
cd /etc/systemd/system/
rm Do.service
rm regis.service

echo -e "UNTUK CREATE DROPLET"
read -p "Masukkan Token DO :" token_do

echo -e "UNTUK REGIS IP"
read -p "Masukkan Token Github : " token_git
read -p "Masukkan Token Telegram : " token_tele1
echo -e "Mengambil Informasi Token"
sleep 2

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
sed -i "s/{TOKEN_GITHUB}/$TOKEN_GITHUB/g" regis.py
TOKEN_TELEGRAM="$token_tele1"
sed -i "s/{TOKEN_TELEGRAM}/$TOKEN_TELEGRAM/g" regis.py

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

cd
rm setup1.sh
