#!/bin/bash

echo -e "UNTUK CREATE DROPLET"
read -p "Masukkan Token DO :" token_do
read -p "Masukkan Token Telegram : " token_tele
sleep 2

wget https://raw.githubusercontent.com/Paper890/crdrop/main/Do.py

# FOR DO CREATE
TOKEN_DO="$token_do"
sed -i "s/{TOKEN_DO}/$TOKEN_DO/g" Do.py
TOKEN_TELEGRAM="$token_tele"
sed -i "s/{TOKEN_TELEGRAM}/$TOKEN_TELEGRAM/g" Do.py

echo "Instalasi selesai."

cd
rm setupdo.sh
