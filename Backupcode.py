import requests
import json
import time
import random
import string
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import schedule

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

# Fungsi untuk menghasilkan nama droplet acak
def generate_random_name():
    random_id = 'ID' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    random_text = ' '.join(random.choices(string.ascii_lowercase, k=2))
    return f"{random_id}-{random_text}"

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

# Fungsi untuk mengedit droplet
def edit_droplet(token, droplet_id, new_size):
    url = f"https://api.digitalocean.com/v2/droplets/{droplet_id}/resize"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        "type": "resize",
        "size": new_size
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.status_code == 204

# Fungsi untuk menghapus droplet berdasarkan ID droplet
def delete_droplet(token, droplet_id):
    url = f"https://api.digitalocean.com/v2/droplets/{droplet_id}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.delete(url, headers=headers)
    return response.status_code == 204

# Fungsi untuk mendapatkan daftar droplet dan memeriksa usia setiap droplet
def check_and_delete_droplets(token):
    url = "https://api.digitalocean.com/v2/droplets"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        droplets = response.json()["droplets"]
        for droplet in droplets:
            created_at = droplet["created_at"]
            created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            current_date = datetime.utcnow()
            age = current_date - created_date
            if age.days >= 30:
                droplet_id = droplet["id"]
                delete_droplet(token, droplet_id)

# Fungsi untuk menjalankan check_and_delete_droplets setiap hari
def job():
    check_and_delete_droplets('TOKEN_DO')

# Schedule job untuk dijalankan setiap hari
schedule.every().day.do(job)

# Fungsi untuk menangani perintah /start
def start(update, context):
    update.message.reply_text('Selamat Menggunakan Bot Ini, Beberapa Command yang bisa kamu gunakan Diantaranya: /create (Buat droplet) /delete (Delete Droplet).')

# Fungsi untuk menangani pesan yang diterima
def echo(update, context):
    update.message.reply_text(update.message.text)

# Fungsi untuk menangani perintah /create
def create_droplet_command(update, context):
    update.message.reply_text("Silakan masukkan nama droplet:")
    return "NAME"

# Fungsi untuk menangani nama droplet
def handle_name(update, context):
    context.user_data['name'] = generate_random_name()
    update.message.reply_text("Negara: sg1 (Singapura)")
    update.message.reply_text(f"Nama droplet Anda: {context.user_data['name']}")
    return "REGION"

# Fungsi untuk menangani wilayah droplet
def handle_region(update, context):
    context.user_data['region'] = "sg1"
    update.message.reply_text("Negara: sg1 (Singapura)")
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
    token = 'TOKEN_DO'  # Token API DigitalOcean Anda
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
            message = "Informasi Droplet:\n"
            message += f"`ID:` `{droplet_info['id']}`\n"
            message += "Nama: " + droplet_info['name'] + "\n"
            message += "Status: " + droplet_info['status'] + "\n"
            message += f"`Alamat IP:` `{droplet_info['ip_address']}`"
            update.message.reply_text(message, parse_mode="MarkdownV2")
        else:
            update.message.reply_text("Gagal mendapatkan informasi droplet.")
    else:
        update.message.reply_text("Gagal membuat droplet.")

    return ConversationHandler.END

# Fungsi untuk menangani perintah /edit
def edit_droplet_command(update, context):
    update.message.reply_text("Silakan masukkan ID droplet yang ingin diedit:")
    return "EDIT_DROPLET_ID"

# Fungsi untuk menangani ID droplet yang ingin diedit
def handle_edit_droplet_id(update, context):
    context.user_data['edit_droplet_id'] = update.message.text
    update.message.reply_text("Silakan masukkan ukuran RAM baru untuk droplet (1GB, 2GB, 4GB, atau 8GB):")
    return "NEW_SIZE"

# Fungsi untuk menangani ukuran RAM baru droplet
def handle_new_size(update, context):
    context.user_data['new_size'] = update.message.text
    update.message.reply_text("Sedang memproses pengeditan droplet...")
    token = 'TOKEN_DO'  # Token API DigitalOcean Anda
    droplet_id = context.user_data['edit_droplet_id']
    new_size = context.user_data['new_size']
    time.sleep(60)  # Menunda selama 1 menit
    if edit_droplet(token, droplet_id, convert_size(new_size)):
        update.message.reply_text(f"Droplet dengan ID {droplet_id} berhasil diubah menjadi ukuran {new_size}.")
    else:
        update.message.reply_text("Gagal mengedit droplet. Pastikan ID droplet dan ukuran baru benar.")
    return ConversationHandler.END

# Fungsi untuk menangani perintah /delete
def delete_droplet_command(update, context):
    update.message.reply_text("Silakan masukkan ID droplet yang ingin dihapus:")
    return "DROPLET_ID"

# Fungsi untuk menangani ID droplet yang ingin dihapus
def handle_droplet_id(update, context):
    context.user_data['droplet_id'] = update.message.text
    token = 'TOKEN_DO'  # Token API DigitalOcean Anda
    droplet_id = context.user_data['droplet_id']
    if delete_droplet(token, droplet_id):
        update.message.reply_text(f"Droplet dengan ID {droplet_id} berhasil dihapus.")
    else:
        update.message.reply_text("Gagal menghapus droplet. Pastikan ID droplet benar.")
    return ConversationHandler.END

def main():
    updater = Updater('TOKEN_TELEGRAM', use_context=True)  # Token bot Telegram Anda

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

    conv_handler_delete = ConversationHandler(
        entry_points=[CommandHandler('delete', delete_droplet_command)],
        states={
            "DROPLET_ID": [MessageHandler(Filters.text, handle_droplet_id)]
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler_delete)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    # Mulai scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

    updater.idle()

if __name__ == '__main__':
    main()

                
