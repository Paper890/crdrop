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


######№####

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
