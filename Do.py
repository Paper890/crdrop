import requests
import json
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Dictionary untuk logaritma pengimputan size
size_mapping = {
    '1gb': 's-1vcpu-1gb-amd',
    '2gb': 's-1vcpu-2gb-amd',
    '4gb': 's-2vcpu-4gb-amd',
    '8gb': 's-4vcpu-8gb-amd'
}

# Dictionary untuk logaritma pengimputan image
image_mapping = {
    'ub20': 'ubuntu-20-04-x64',
    'deb10': 'debian-10-x64'
}

# Fungsi untuk mengonversi ukuran droplet ke format yang diinginkan
def convert_size(size):
    return size_mapping.get(size.lower())

# Fungsi untuk mengonversi image droplet ke format yang diinginkan
def convert_image(image):
    return image_mapping.get(image.lower())

# Fungsi untuk membuat droplet DigitalOcean
def create_droplet(token, name, region, size, image, password):
    url = "https://api.digitalocean.com/v2/droplets"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    user_data_script = f'#!/bin/bash\n\nuseradd -m -s /bin/bash user\n' \
                       f'echo -e "{password}\\n{password}" | passwd user\n' \
                       f'echo -e "{password}\\n{password}" | passwd root\n'
    data = {
        "name": name,
        "region": region,
        "size": convert_size(size),
        "image": convert_image(image),
        "ssh_keys": None,
        "backups": False,
        "ipv6": False,
        "user_data": user_data_script,
        "private_networking": None,
        "volumes": None,
        "tags": []
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 202:
        return True, response.json()["droplet"]["id"]
    else:
        return False, None

# Fungsi untuk mendapatkan informasi tentang droplet yang sudah dibuat
def get_droplet_info(token, droplet_id):
    url = f"https://api.digitalocean.com/v2/droplets/{droplet_id}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["droplet"]["networks"]["v4"]:
            droplet_info = {
                "id": data["droplet"]["id"],
                "name": data["droplet"]["name"],
                "status": data["droplet"]["status"],
                "ip_address": data["droplet"]["networks"]["v4"][0]["ip_address"]
            }
            return droplet_info
    return None

# Fungsi untuk menangani perintah /start
def start(update, context):
    update.message.reply_text('Halo! Saya adalah bot sederhana. Kirimkan pesan kepada saya.')

# Fungsi untuk menangani pesan yang diterima
def echo(update, context):
    update.message.reply_text(update.message.text)

# Fungsi untuk menangani perintah /create_droplet
def create_droplet_command(update, context):
    update.message.reply_text("Silakan masukkan nama droplet:")
    return "NAME"

# Fungsi untuk menangani nama droplet
def handle_name(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text("Silakan masukkan wilayah droplet:")
    return "REGION"

# Fungsi untuk menangani wilayah droplet
def handle_region(update, context):
    context.user_data['region'] = update.message.text
    update.message.reply_text("Silakan masukkan ukuran droplet (1GB, 2GB, 4GB, atau 8GB):")
    return "SIZE"

# Fungsi untuk menangani ukuran droplet
def handle_size(update, context):
    context.user_data['size'] = update.message.text
    update.message.reply_text("Silakan masukkan jenis image droplet (ub20 untuk Ubuntu 20.04 atau deb10 untuk Debian 10):")
    return "IMAGE"

# Fungsi untuk menangani image droplet
def handle_image(update, context):
    context.user_data['image'] = update.message.text
    update.message.reply_text("Silakan masukkan password untuk droplet:")
    return "PASSWORD"

# Fungsi untuk menangani password droplet dan membuat droplet
def handle_password(update, context):
    token = 'YOUR_DIGITALOCEAN_API_TOKEN'  # Token API DigitalOcean Anda
    password = update.message.text

    name = context.user_data['name']
    region = context.user_data['region']
    size = context.user_data['size']
    image = context.user_data['image']

    success, droplet_id = create_droplet(token, name, region, size, image, password)
    if success:
        update.message.reply_text("Droplet berhasil dibuat. Menunggu informasi droplet...")
        time.sleep(60)  # Menunda selama 1 menit
        
        droplet_info = get_droplet_info(token, droplet_id)
        if droplet_info:
            update.message.reply_text("Informasi Droplet:")
            update.message.reply_text("ID: " + str(droplet_info["id"]))
            update.message.reply_text("Nama: " + droplet_info["name"])
            update.message.reply_text("Status: " + droplet_info["status"])
            update.message.reply_text("Alamat IP: " + droplet_info["ip_address"])
        else:
            update.message.reply_text("Gagal mendapatkan informasi droplet.")
    else:
        update.message.reply_text("Gagal membuat droplet.")

    return ConversationHandler.END

def main():
    updater = Updater('YOUR_TELEGRAM_BOT_TOKEN', use_context=True)  # Token bot Telegram Anda

    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create_droplet_command)],
        states={
            "NAME": [MessageHandler(Filters.text, handle_name)],
            "REGION": [MessageHandler(Filters.text, handle_region)],
            "SIZE": [MessageHandler(Filters.regex(r'^(1GB|2GB|4GB|8GB)$'), handle_size)],
            "IMAGE": [MessageHandler(Filters.regex(r'^(ub20|deb10)$'), handle_image)],
            "PASSWORD": [MessageHandler(Filters.text, handle_password)]
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
