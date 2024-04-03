import digitalocean
import logging
import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Token API dari Digital Ocean
digital_ocean_token = 'TOKEN'
# Token Bot Telegram
telegram_bot_token = 'TOKEN'

# Konfigurasi logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def simplify_parameters(region_short, ram_size):
    # Mendefinisikan pemetaan dari input sederhana ke parameter Digital Ocean
    region_mapping = {
        'sg': 'sgp1',  # Singapura
        'ny': 'nyc1',  # New York
        'sf': 'sfo1',  # San Francisco
        # Tambahkan lebih banyak sesuai kebutuhan
    }
    
    size_slug_mapping = {
         1: 's-1vcpu-1gb',
         2: 's-1vcpu-2gb',
         4: 's-2vcpu-4gb',
         8: 's-4vcpu-8gb',
    # Tambahkan lebih banyak sesuai kebutuhan
    }

    # Mendapatkan parameter sesuai input
    region = region_mapping.get(region_short.lower(), 'sgp1')  # Default ke Singapura jika tidak ditemukan
    size_slug = size_slug_mapping.get(ram_size, 's-1vcpu-1gb')  # Default ke 1GB RAM jika tidak ditemukan
    
    # Kita akan menggunakan image Ubuntu 20.04 sebagai default
    image = 'ubuntu-20-04-x64'
    
    # Nama droplet bisa di-generate secara dinamis atau diminta dari pengguna
    name = f"droplet-{region}-{ram_size}gb"
    
    return name, region, image, size_slug

def create_droplet(update: Update, context: CallbackContext) -> None:
    manager = digitalocean.Manager(token=digital_ocean_token)
    
    # Mendapatkan input dari pengguna
    region_short = context.args[0] if context.args else 'sg'
    ram_size = int(context.args[1]) if len(context.args) > 1 else 1
    
    # Mendapatkan parameter yang telah disederhanakan
    name, region, image, size_slug = simplify_parameters(region_short, ram_size)
    
    droplet = digitalocean.Droplet(token=digital_ocean_token,
                                   name=name,
                                   region=region,
                                   image=image,
                                   size_slug=size_slug)
    droplet.create()
    
    # Menyimpan tanggal pembuatan droplet
    now = datetime.datetime.now()
    droplet.created_at = now
    
    update.message.reply_text('Droplet berhasil dibuat!')

def delete_droplet(update: Update, context: CallbackContext) -> None:
    droplet_id = context.args[0] if context.args else ''
    if droplet_id:
        droplet = digitalocean.Droplet(token=digital_ocean_token, id=droplet_id)
        droplet.destroy()
        update.message.reply_text(f'Droplet dengan ID {droplet_id} berhasil dihapus!')
    else:
        update.message.reply_text('Mohon masukkan ID Droplet yang ingin dihapus.')

def delete_old_droplets(context: CallbackContext) -> None:
    manager = digitalocean.Manager(token=digital_ocean_token)
    my_droplets = manager.get_all_droplets()
    
    # Mendapatkan tanggal sekarang
    now = datetime.datetime.now()
    
    for droplet in my_droplets:
        created_at = droplet.created_at
        age = now - created_at
        
        # Menghapus droplet yang berusia lebih dari 30 hari
        if age.days >= 30:
            droplet.destroy()
            logger.info(f'Droplet dengan ID {droplet.id} dihapus karena telah berusia 30 hari.')

def main():
    updater = Updater(telegram_bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("createdroplet", create_droplet))
    dispatcher.add_handler(CommandHandler("deletedroplet", delete_droplet))
    
    # Menambahkan scheduler untuk menjalankan penghapusan droplet setiap hari
    job_queue = updater.job_queue
    job_queue.run_daily(delete_old_droplets, time=datetime.time(hour=0, minute=0, second=0))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
