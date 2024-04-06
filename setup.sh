#!/bin/bash

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
wget https://domain.com/path/to/your_script.py -P san/script/bot/

# Ganti nilai teks dalam skrip Python
MY_TEXT="Nilai yang Anda inginkan"
sed -i "s/{MY_TEXT}/$MY_TEXT/g" your_script.py

echo "Instalasi selesai."
