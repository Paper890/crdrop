import datetime
import random
import re
import requests
import base64
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def start(update, context):
    update.message.reply_text('🤖Bot Registrasi Autoscript By San🤖 \n📝Masukkan /newsc untuk Registrasi')

def add_text(update, context):
    context.user_data['addtext'] = True
    update.message.reply_text("Masukkan Masa Aktif dan IP. Contoh : 10 192.168.1.1")

def generate_user():
    random_id = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
    return f"ID{random_id}"

def calculate_expiry(days):
    today = datetime.datetime.now()
    target_date = today + datetime.timedelta(days=days)
    return target_date.strftime('%Y-%m-%d')

def echo(update, context):
    if 'addtext' in context.user_data and context.user_data['addtext']:
        text = update.message.text
        ip = text.split()[-1]  # Mengambil IP address dari input
        days = int(text.split()[0])  # Mengambil jumlah hari dari input
        user = generate_user()
        expiry_date = calculate_expiry(days)
        add_text_to_file(github_username, github_repository, file_name, f"### {user} {expiry_date} {ip}", github_token)
        update.message.reply_text("✅ Registrasi Berhasil :)")
        del context.user_data['addtext']
    else:
        update.message.reply_text(update.message.text)

def add_text_to_file(username, repository, filename, text, token):
    url = f"https://api.github.com/repos/{username}/{repository}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()['content']
        existing_text = base64.b64decode(content).decode('utf-8')
    else:
        print("Failed to get file content.")
        return

    new_text = existing_text + "\n" + text

    data = {
        "message": "Add text to file",
        "content": base64.b64encode(new_text.encode()).decode(),
        "sha": response.json()['sha']
    }
    put_response = requests.put(url, headers=headers, json=data)
    if put_response.status_code == 200:
        print("Text added to file successfully.")
    else:
        print("Failed to add text to file.")

def main():
    bot_token = '{TOKEN_TELEGRAM}'

    global github_username, github_repository, file_name, github_token
    github_username = 'Paper890'
    github_repository = 'san'
    file_name = 'izin'
    github_token = '{TOKEN_GITHUB}'

    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("newsc", add_text))
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
