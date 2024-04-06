#!/bin/bash

read -p "Masukkan Token DO :" token_do
read -p "Masukkan Token Telegram : " token_tele
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

# Ganti nilai teks dalam skrip Python
TOKEN_DO="$token_do"
sed -i "s/{TOKEN_DO}/$TOKEN_DO/g" Do.py
TOKEN_TELEGRAM="$token_tele"
sed -i "s/{TOKEN_TELEGRAM}/$TOKEN_TELEGRAM/g" Do.py

echo "Instalasi selesai."
