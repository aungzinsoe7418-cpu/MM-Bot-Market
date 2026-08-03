import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Render Port Check Web Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- Telegram Bot Code ---
import logging
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)
# 1. Telegram Admin Chat ID & Developer Username
ADMIN_CHAT_ID = "8582190375"
DEVEL_USERNAME = "superraizo7"

# 2. Telegram Bot Token
BOT_TOKEN = "     import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Render Port Check Web Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- Telegram Bot Code ---
import logging
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)

# 1. Telegram Admin Chat ID & Developer Username
ADMIN_CHAT_ID = "8582190375"
DEVEL_USERNAME = "superraizo7"

# 2. Telegram Bot Token
BOT_TOKEN =
"8912157146:AAftkWXLHV6gqqiBPaYdBBuk1ffTls7I3Zc"

# Database Setup
def init_db():
    conn = sqlite3.connect('mm_bot_market.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT,
                    user_id INTEGER,
                    name TEXT,
                    username TEXT,
                    details TEXT,
                    status TEXT,
                    date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 Bot မှာယူရန်", callback_data="order_bot")],
        [InlineKeyboardButton("🎮 Game Top-up Bot", callback_data="topup_bot")],
        [InlineKeyboardButton("📞 ဆက်သွယ်ရန်", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 *MM Bot Market* မှ ကြိုဆိုပါတယ်ဗျာ!\n\nအောက်ပါ Menu များမှ လိုအပ်သည်များကို ရွေးချယ်နိုင်ပါသည်။",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Button Click Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "order_bot":
        await query.edit_message_text(text="ကျေးဇူးပြု၍ လိုချင်သော Bot ပုံစံကို ရေးပြပေးပါ။")
    elif query.data == "topup_bot":
        await query.edit_message_text(text="Game Top-up ဝန်ဆောင်မှု မကြာမီ စတင်ပါမည်။")
    elif query.data == "contact":
        await query.edit_message_text(text=f"Developer: @{DEVEL_USERNAME} သို့ ဆက်သွယ်နိုင်ပါသည်။")

# Main Function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
       "

# Database Setup
def init_db():
    conn = sqlite3.connect('mm_bot_market.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT,
                    user_id INTEGER,
                    name TEXT,
                    username TEXT,
                    details TEXT,
                    status TEXT,
                    date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 Bot မှာယူရန်", callback_data="order_bot")],
        [InlineKeyboardButton("🎮 Game Top-up Bot", callback_data="topup_bot")],
        [InlineKeyboardButton("📞 ဆက်သွယ်ရန်", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 *MM Bot Market* မှ ကြိုဆိုပါတယ်ဗျာ!\n\nအောက်ပါ Menu များမှ လိုအပ်သည်များကို ရွေးချယ်နိုင်ပါသည်။",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Button Click Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "order_bot":
        await query.edit_message_text(text="ကျေးဇူးပြု၍ လိုချင်သော Bot ပုံစံကို ရေးပြပေးပါ။")
    elif query.data == "topup_bot":
        await query.edit_message_text(text="Game Top-up ဝန်ဆောင်မှု မကြာမီ စတင်ပါမည်။")
    elif query.data == "contact":
        await query.edit_message_text(text=f"Developer: @{DEVEL_USERNAME} သို့ ဆက်သွယ်နိုင်ပါသည်။")

# Main Function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
