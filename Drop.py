import digitalocean
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Token API dari Digital Ocean
digital_ocean_token = 'Token'
# Token Bot Telegram
telegram_bot_token = 'token'

# Konfigurasi logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Fungsi untuk membuat droplet
def create_droplet(update: Update, context: CallbackContext) -> None:
    manager = digitalocean.Manager(token=digital_ocean_token)
    droplet = digitalocean.Droplet(token=digital_ocean_token,
                                   name='ExampleDroplet',
                                   region='nyc3', # New York 3
                                   image='ubuntu-20-04-x64', # Ubuntu 20.04
                                   size_slug='s-1vcpu-1gb') # 1GB RAM, 1 vCPU
    droplet.create()
    update.message.reply_text('Droplet berhasil dibuat!')

# Fungsi untuk menghapus droplet
def delete_droplet(update: Update, context: CallbackContext) -> None:
    droplet_id = context.args[0] if context.args else ''
    if droplet_id:
        droplet = digitalocean.Droplet(token=digital_ocean_token, id=droplet_id)
        droplet.destroy()
        update.message.reply_text(f'Droplet dengan ID {droplet_id} berhasil dihapus!')
    else:
        update.message.reply_text('Mohon masukkan ID Droplet yang ingin dihapus.')

# Fungsi utama
def main():
    updater = Updater(telegram_bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("createdroplet", create_droplet))
    dispatcher.add_handler(CommandHandler("deletedroplet", delete_droplet))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
