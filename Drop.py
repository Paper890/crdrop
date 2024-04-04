import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from datetime import datetime, timedelta

# State untuk konversasi membuat droplet dengan nama, password, size, dan image
NAMA, PASSWORD, UKURAN, GAMBAR, NOTIFIKASI = range(5)

# Fungsi untuk menangani perintah /start
def start(update, context):
    update.message.reply_text('Create Droplet DO. Masukkan Username:')
    return NAMA

# Fungsi untuk menangani nama droplet
def nama_droplet(update, context):
    context.user_data['nama_droplet'] = update.message.text
    update.message.reply_text('Password')
    return PASSWORD

# Fungsi untuk menangani password droplet
def password_droplet(update, context):
    context.user_data['password'] = update.message.text
    update.message.reply_text('Imput Ram (contoh: 1gb, 2gb, dll):')
    return UKURAN

# Fungsi untuk menangani ukuran droplet dengan input yang lebih simpel
def ukuran_droplet(update, context):
    ukuran = update.message.text.lower()
    ukuran_droplet_mapping = {
        '1gb': 's-1vcpu-1gb',
        '2gb': 's-1vcpu-2gb',
        '4gb': 's-2vcpu-4gb',
        '8gb': 's-4vcpu-8gb',
        '16gb': 's-8vcpu-16gb',
        '32gb': 's-16vcpu-32gb',
        '64gb': 's-32vcpu-64gb',
        '128gb': 's-48vcpu-128gb',
        '224gb': 's-64vcpu-224gb'
    }
    if ukuran in ukuran_droplet_mapping:
        context.user_data['ukuran_droplet'] = ukuran_droplet_mapping[ukuran]
        update.message.reply_text('Imput OS VPS (opsi: ub20, deb10')
        return GAMBAR
    else:
        update.message.reply_text('Ukuran droplet tidak valid. Silakan masukkan ukuran yang valid (contoh: 1gb, 2gb, dll):')
        return UKURAN

# Fungsi untuk menangani image droplet dengan input yang lebih simpel
def image_droplet(update, context):
    image = update.message.text.lower()
    image_droplet_mapping = {
        'ub20': 'ubuntu-20-04-x64',
        'deb10': 'debian-10-x64'
    }
    if image in image_droplet_mapping:
        context.user_data['image_droplet'] = image_droplet_mapping[image]
        update.message.reply_text('Terima kasih! Droplet Anda sedang dibuat.')
        create_droplet(update, context)  # Langsung membuat droplet setelah image diinput
        return ConversationHandler.END
    else:
        update.message.reply_text('Image droplet tidak valid. Silakan masukkan image yang valid (contoh: ub20, deb10, dll):')
        return GAMBAR

# Fungsi untuk membuat droplet dengan semua informasi yang diberikan
def create_droplet(update, context):
    nama_droplet = context.user_data['nama_droplet']
    password = context.user_data['password']
    ukuran_droplet = context.user_data['ukuran_droplet']
    gambar = context.user_data['image_droplet']

    # Token API DigitalOcean Anda
    do_token = 'TOKEN_API_DO_ANDA'

    # Konfigurasi payload untuk membuat droplet dengan semua informasi yang diberikan
    payload = {
        'name': nama_droplet,
        'region': 'nyc1',  # Ganti sesuai kebutuhan
        'size': ukuran_droplet,
        'image': gambar,
        'ssh_keys': None,
        'backups': False,
        'ipv6': False,
        'user_data': None,
        'private_networking': None,
        'volumes': None,
        'tags': ['telegram-bot'],  # Ganti sesuai kebutuhan
        'user_data': f'#!/bin/bash\n\nsudo passwd root <<< {password}\n'
    }

    # Endpoint untuk membuat droplet
    url = 'https://api.digitalocean.com/v2/droplets'

    # Header yang dibutuhkan untuk autentikasi
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {do_token}'
    }

    # Membuat permintaan POST ke API DigitalOcean
    response = requests.post(url, json=payload, headers=headers)

    # Menangani respons dari API
    if response.status_code == 202:
        droplet_info = response.json()['droplet']
        ip_address = droplet_info['networks']['v4'][0]['ip_address']
        image = droplet_info['image']['slug']
        ram = droplet_info['memory']
        root_password = password
        message = f'Info Droplet:\nIP Address: {ip_address}\nImage: {image}\nRAM: {ram}\nRoot Password: {root_password}'
        update.message.reply_text('Droplet berhasil dibuat! Berikut informasi VPS Anda:\n' + message)
    else:
        update.message.reply_text('Gagal membuat droplet.')

    return ConversationHandler.END

# Fungsi untuk mendapatkan informasi tentang semua droplet yang dimiliki pengguna
def get_all_droplets(api_token):
    url = 'https://api.digitalocean.com/v2/droplets'
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['droplets']
    else:
        print('Gagal mengambil informasi droplet:', response.text)
        return None

# Fungsi untuk memeriksa usia droplet dan menghapus yang sudah berusia 30 hari
def delete_old_droplets(api_token):
    droplets = get_all_droplets(api_token)
    if droplets:
        for droplet in droplets:
            created_at = datetime.fromisoformat(droplet['created_at'][:-1])  # Menghapus Z dari akhir string
            current_time = datetime.now()
            age = current_time - created_at
            if age.days >= 30:
                droplet_id = droplet['id']
                delete_droplet(api_token, droplet_id)

# Fungsi untuk menghapus droplet berdasarkan ID
def delete_droplet(api_token, droplet_id):
    url = f'https://api.digitalocean.com/v2/droplets/{droplet_id}'
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f'Droplet dengan ID {droplet_id} berhasil dihapus.')
    else:
        print(f'Gagal menghapus droplet dengan ID {droplet_id}:', response.text)

def main():
    # Inisialisasi updater dengan token bot
    updater = Updater("TOKEN_BOT_ANDA", use_context=True)

    # Mendapatkan dispatcher untuk mendaftarkan handler
    dp = updater.dispatcher

    # Mendefinisikan handler konversasi
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAMA: [MessageHandler(Filters.text & ~Filters.command, nama_droplet)],
            PASSWORD: [MessageHandler(Filters.text & ~Filters.command, password_droplet)],
            UKURAN: [MessageHandler(Filters.text & ~Filters.command, ukuran_droplet)],
            GAMBAR: [MessageHandler(Filters.text & ~Filters.command, image_droplet)],
        },
        fallbacks=[]
    )

    # Mendaftarkan handler konversasi ke dispatcher
    dp.add_handler(conv_handler)

    # Memanggil fungsi untuk memeriksa dan menghapus droplet berusia 30 hari
    do_api_token = 'TOKEN_API_DO_ANDA'
    delete_old_droplets(do_api_token)

    # Mulai polling untuk memeriksa pesan baru dari Telegram
    updater.start_polling()

    # Menjaga bot berjalan hingga pengguna menghentikannya secara manual
    updater.idle()

if __name__ == '__main__':
    main()
  
