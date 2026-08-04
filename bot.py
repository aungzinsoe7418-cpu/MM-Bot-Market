import os
import csv
import html
import logging
import sqlite3
import threading
import traceback
import asyncio

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    CallbackQueryHandler
)


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================================================
# KEEP ALIVE SERVER (Background Web Server)
# ==========================================================

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MM Bot Market is Active!")
        
    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    logging.info(f"Keep Alive Server Running on port {port}")
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()


# ==========================================================
# CONFIGURATION
# ==========================================================

ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8582190375"))
DEVELOPER_USERNAME = "superraizo7"
DEMO_BOT_USERNAME = "OnlineshopDemo88_bot"

BOT_TOKEN = os.environ.get("BOT_TOKEN")


# ==========================================================
# CONVERSATION STATES
# ==========================================================

PACKAGE_TYPE, BOT_TYPE, DESCRIPTION, FEATURES, CUSTOMER_INFO, BUDGET = range(6)


# ==========================================================
# DATABASE (WITH WAL MODE FOR HIGH PERFORMANCE)
# ==========================================================

DB_NAME = "mm_bot_market.db"

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            joined_date TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            user_id INTEGER,
            name TEXT,
            username TEXT,
            customer_info TEXT,
            bot_type TEXT,
            description TEXT,
            features TEXT,
            budget TEXT,
            status TEXT,
            created_date TEXT,
            updated_date TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            rating TEXT,
            created_date TEXT
        )
        """
    )
    conn.commit()
    conn.close()

init_db()


# ==========================================================
# MAIN MENU
# ==========================================================

def get_main_menu():
    keyboard = [
        ["🤖 ဝန်ဆောင်မှုများ", "💰🤖 ဈေးနှုန်းများ"],
        ["🎬 Demo Bot စမ်းသုံးကြည့်ရန်", "🛒 Bot မှာယူရန်"],
        ["⭐ Customer Review", "❓ FAQ"],
        ["📦 My Order Status", "🧑‍💻 Developer (စောက်ချောကြီး) နှင့် ဆွေးနွေးရန်"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ==========================================================
# START & MAIN BUTTONS
# ==========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else "No Username"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, name, username, joined_date) VALUES (?, ?, ?, ?)",
        (user.id, user.first_name, username, current_date)
    )
    conn.commit()
    conn.close()

    text = (
        "🤖 **MM Bot Market မှ ကြိုဆိုပါတယ်**\n\n"
        "သင့် Business အတွက် Professional Telegram Bot များကို စိတ်ကြိုက် ဖန်တီးပေးပါတယ်။\n\n"
        "✨ **အထူးဝန်ဆောင်မှု:** Bot မှာယူရာတွင် **ငွေကြိုပေးရန် လုံးဝ မလိုပါ**။ Bot ရေးဆွဲပြီးစီး၍ စိတ်ကြိုက် စမ်းသပ်ပြီးမှသာ ငွေချေရမည် ဖြစ်ပါသည်။\n\n"
        "ကျွန်ုပ်တို့ ဖန်တီးပေးနိုင်သော Bot များ👇\n\n"
        "🛒 Online Shop Bot\n"
        "🎮 Game Top-up Bot\n"
        "📢 Telegram Channel Bot\n"
        "🤖 AI Chat Bot\n"
        "🏢 Business Automation Bot\n"
        "✍️ Custom Bot\n\n"
        "အချိန်မရွေး မေးမြန်းစုံစမ်းနိုင်ပါသည် 👇"
    )
    await update.message.reply_text(
        text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


# ==========================================================
# SERVICES
# ==========================================================

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🤖 Telegram Shop Bot", "🎮 Game Top-up Bot"],
        ["📢 Channel Management Bot", "🤖 AI Chat Bot"],
        ["🏢 Business Automation Bot", "⚙️ Custom Telegram Bot"],
        ["🔙 နောက်ပြန်ဆုပ်ရန်"]
    ]
    await update.message.reply_text(
        "🛠️ ကျေးဇူးပြု၍ လေ့လာလိုသော ဝန်ဆောင်မှုကို ရွေးချယ်ပါ 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def service_shop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 **Telegram Shop Bot**\n\n"
        "➡️ Online Shop တွေအတွက် Telegram ကနေ အော်ဒါလက်ခံ၊ ဈေးနှုန်းပြ၊ ငွေပေးချေမှုအချက်အလက်ပြပြီး Customer နဲ့ စနစ်တကျ ဆက်သွယ်နိုင်တဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "🪧 ပါဝင်နိုင်တဲ့ Function များ👇\n"
        "🛍️ Product Catalog — ကုန်ပစ္စည်းစာရင်း\n"
        "🛒 Add to Cart — ခြင်းထဲထည့်ရန်\n"
        "📝 Order Form — အော်ဒါဖြည့်ရန်\n"
        "💳 Payment Info — ငွေပေးချေနည်း\n"
        "📦 Order Tracking — အော်ဒါစစ်ရန်\n"
        "🔔 Admin Notification — Admin အသိပေး\n\n"
        "💡 *မှာယူရာတွင် ငွေကြိုရှင်းရန် မလိုပါ၊ Bot စမ်းသပ်ပြီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def service_game_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 **Game Top-up Bot**\n\n"
        "➡️ eFootball, MLBB, Free Fire စတဲ့ Game တွေအတွက် Top-up Order တွေကို အလိုအလျောက် လက်ခံပေးတဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "🪧 ပါဝင်နိုင်တဲ့ Function များ👇\n"
        "🎯 Game Selection — ဂိမ်းရွေးရန်\n"
        "💎 Package Selection — Package ရွေးရန်\n"
        "🆔 User ID Input — ID ထည့်ရန်\n"
        "🖼️ Payment Screenshot — Screenshot တင်ရန်\n"
        "🧾 Order ID — အော်ဒါနံပါတ်\n"
        "🔔 Admin Alert — Admin အသိပေး\n\n"
        "💡 *မှာယူရာတွင် ငွေကြိုရှင်းရန် မလိုပါ၊ Bot စမ်းသပ်ပြီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def service_channel_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📢 **Channel Management Bot**\n\n"
        "➡️ Telegram Channel Owner တွေအတွက် Channel ကို အလွယ်တကူ စီမံခန့်ခွဲနိုင်တဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "🪧 ပါဝင်နိုင်တဲ့ Function များ👇\n"
        "👋 Auto Welcome — အလိုအလျောက် ကြိုဆို\n"
        "💬 Auto Reply — အလိုအလျောက် ဖြေကြား\n"
        "📅 Scheduled Posts — အချိန်သတ်မှတ်တင်\n"
        "📊 Member Statistics — Member စာရင်း\n"
        "📢 Broadcast — Followers အားလုံးသို့ပို့\n"
        "🛡️ Spam Filter — Spam ကာကွယ်\n\n"
        "💡 *မှာယူရာတွင် ငွေကြိုရှင်းရန် မလိုပါ၊ Bot စမ်းသပ်ပြီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def service_ai_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 **AI Chat Bot**\n\n"
        "➡️ လူ နဲ့ စကားပြောနိုင်တဲ့ Bot ဖြစ်ပြီး Customer Support, FAQ နဲ့ Information တွေကို အလိုအလျောက် ဖြေပေးနိုင်ပါတယ်။\n\n"
        "🪧 ပါဝင်နိုင်တဲ့ Function များ👇\n"
        "💬 AI Chat — AI စကားပြော\n"
        "❓ FAQ Answer — မေးခွန်းဖြေ\n"
        "🌐 Multi-language — ဘာသာစကားများထည့်သွင်းခြင်း\n"
        "🖼️ Image Analysis — ပုံခွဲခြမ်းလေ့လာခြင်း\n"
        "💡 Smart Suggestions — အကြံပြုချက်\n\n"
        "💡 *မှာယူရာတွင် ငွေကြိုရှင်းရန် မလိုပါ၊ Bot စမ်းသပ်ပြီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def service_business_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🏢 **Business Automation Bot**\n\n"
        "➡️ စီးပွားရေးလုပ်ငန်းတွေမှာ လူလုပ်ရတဲ့ အလုပ်တွေကို အလိုအလျောက်လုပ်ပေးတဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "🪧 ပါဝင်နိုင်တဲ့ Function များ👇\n"
        "👤 Customer Registration — စာရင်းသွင်း\n"
        "📅 Appointment Booking — ရက်ချိန်းယူ\n"
        "🧾 Invoice Notification — ဘောက်ချာပို့\n"
        "📈 Daily Reports — နေ့စဉ်အစီရင်ခံ\n"
        "⏰ Payment Reminder — ငွေပေးသတိပေး\n\n"
        "💡 *မှာယူရာတွင် ငွေကြိုရှင်းရန် မလိုပါ၊ Bot စမ်းသပ်ပြီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def service_custom_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚙️ **Custom Telegram Bot**\n\n"
        "➡️ Customer လိုချင်တဲ့ Function အတိုင်း အစကနေ အထူးရေးသားပေးတဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "✨ Custom Features — စိတ်ကြိုက် Function\n"
        "🔗 API Integration — API ချိတ်ဆက်\n"
        "🗄️ Database System — Database စနစ်\n"
        "🔐 User Login — Login စနစ်\n"
        "👨‍💼 Admin Panel — Admin စီမံခန့်ခွဲမှု\n"
        "🚀 Future Upgrade — နောင်တိုးချဲ့နိုင်\n\n"
        "💡 *မှာယူရာတွင် ငွေကြိုရှင်းရန် မလိုပါ၊ Bot စမ်းသပ်ပြီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")


# ==========================================================
# PRICING
# ==========================================================

async def show_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💰🤖 **Bot Development Packages**\n\n"
        "✨ **သတိပြုရန်:** Bot မှာယူသူများအနေဖြင့် **ငွေကြိုရှင်းရန် မလိုပါ**။ Bot ရေးဆွဲပြီးစီးမှ ငွေချေရမည် ဖြစ်ပါသည်။\n\n"
        "🤖 **Starter Package (အခြေခံ Package)**\n"
        "💰➡️ 50,000 – 150,000 MMK\n\n"
        "🤖 **Standard Package (အလယ်အလတ် Package)**\n"
        "💰➡️ 150,000 – 300,000 MMK\n\n"
        "🤖 **Premium Package (အဆင့်မြင့် Package)**\n"
        "💰➡️ 300,000 – 600,000+ MMK\n\n"
        "အောက်ပါခလုတ်မှတစ်ဆင့် လိုအပ်သော Package ကို ရွေးချယ်နိုင်ပါသည် 👇"
    )
    keyboard = [
        ["🤖 Starter Package", "🤖 Standard Package"],
        ["🤖 Premium Package (Customize Bot)"],
        ["🛒 Bot မှာယူရန်", "🔙 နောက်ပြန်ဆုပ်ရန်"]
    ]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def view_starter_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 **Starter Package (အခြေခံ Package)**\n\n"
        "💰➡️ 50,000 – 150,000 MMK\n\n"
        "💬 Auto Reply — အလိုအလျောက် စာပြန် (AR)\n"
        "📋 Simple Menu — ရိုးရှင်းသော Menu (SM)\n"
        "📝 Basic Order Form — အခြေခံ အော်ဒါဖြည့်စနစ် (BOF)\n"
        "🔔 Admin Notification — Admin အသိပေးစနစ် (AN)\n\n"
        "✨ *ငွေကြိုပေးရန် မလိုပါ။ Bot ပြီးစီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["💰🤖 ဈေးနှုန်းများ", "🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def view_standard_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 **Standard Package (အလယ်အလတ် Package)**\n\n"
        "💰➡️ 150,000 – 300,000 MMK\n\n"
        "🛍️ Product Catalog — ကုန်ပစ္စည်းစာရင်း (PC)\n"
        "🛒 Order System — အော်ဒါစနစ် (OS)\n"
        "🖼️ Payment Screenshot — ငွေပေးချေ Screenshot စစ်ဆေးမှု (PS)\n"
        "🗄️ Database — ဒေတာသိမ်းဆည်းစနစ် (DB)\n"
        "👨‍💼 Admin Control — Admin ထိန်းချုပ်မှု (AC)\n\n"
        "✨ *ငွေကြိုပေးရန် မလိုပါ။ Bot ပြီးစီးမှ ငွေချေပါ။*"
    )
    keyboard = [["🛒 Bot မှာယူရန်"], ["💰🤖 ဈေးနှုန်းများ", "🔙 နောက်ပြန်ဆုပ်ရန်"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def view_premium_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 **Premium Package (အဆင့်မြင့် Package)**\n\n"
        "💰➡️ 300,000 – 600,000+ MMK\n\n"
        "⚙️ Advanced Features — အဆင့်မြင့် Function များ (AF)\n"
        "🔗 API Integration — ပြင်ပစနစ် ချိတ်ဆက်မှု (API)\n"
        "🤖 AI Integration — AI စနစ်ထည့်သွင်းမှု (AI)\n"
        "🖥️ Admin Panel — Admin စီမံခန့်ခွဲ Panel (AP)\n"
        "✨ Custom System — စိတ်ကြိုက် System ဖန်တီးမှု (CS)\n\n"
        "✨ *ငွေကြိုပေးရန် မလိုပါ။ Bot ပြီးစီးမှ ငွေချေပါ။*"
    )
    keyboard = [
        ["🛒 Bot မှာယူရန်"],
        ["🚨 🤖 Customize Bot အတွက် Developer (စောက်ချောကြီး) ကို တိုက်ရိုက်ဆက်သွယ်ပါ"],
        ["💰🤖 ဈေးနှုန်းများ", "🔙 နောက်ပြန်ဆုပ်ရန်"]
    ]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")


# ==========================================================
# REDIRECTS, FAQ & REVIEWS
# ==========================================================

async def demo_redirect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎬 Demo Bot စမ်းသုံးရန်", url=f"https://t.me/{DEMO_BOT_USERNAME}")]]
    await update.message.reply_text(
        "အောက်ပါ Button ကို နှိပ်ပြီး Demo Bot ကို စမ်းသပ်နိုင်ပါတယ် 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def developer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🧑‍💻 Developer (စောက်ချောကြီး) နှင့် ဆွေးနွေးရန်", url=f"https://t.me/{DEVELOPER_USERNAME}")]]
    await update.message.reply_text(
        "Developer နှင့် တိုက်ရိုက် ဆွေးနွေးလိုပါက Button ကို နှိပ်ပါ 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ **Frequently Asked Questions**\n\n"
        "Q: Bot မှာယူရင် ငွေကြိုရှင်းပေးရပါသလား?\n"
        "A: **ငွေကြိုရှင်းရန် မလိုပါခင်ဗျာ။** Bot ရေးဆွဲပြီးစီး၍ စိတ်ကြိုက် စမ်းသပ်ပြီးမှသာ ငွေချေရမည် ဖြစ်ပါတယ်။\n\n"
        "Q: Bot ဖန်တီးဖို့ ဘယ်လောက်ကြာပါသလဲ?\n"
        "A: ၃ ရက်မှ ၁၄ ရက်အထိ ကြာနိုင်ပါတယ်။\n\n"
        "Q: ရှိပြီးသား Bot ကို ပြင်ဆင်နိုင်ပါသလား?\n"
        "A: ရပါတယ်။ Update နှင့် Modify ပြုလုပ်ပေးနိုင်ပါတယ်။\n\n"
        "Q: Delivery ပြီးရင် Support ရပါသလား?\n"
        "A: ရပါတယ်။ Basic Support ပေးပါမည်။"
    )
    keyboard = [[InlineKeyboardButton("🧑‍💻 Developer (စောက်ချောကြီး) နှင့် ဆွေးနွေးရန်", url=f"https://t.me/{DEVELOPER_USERNAME}")]]
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, rating, created_date FROM reviews ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    review_text = "⭐ **Customer Reviews & Feedback**\n\n"
    if rows:
        for r in rows:
            review_text += f"👤 {r[0]} | Rating: {r[1]} | 📅 {r[2]}\n"
    else:
        review_text += "✨ ယခုထိ Review ပေးထားသူ မရှိသေးပါ။ Order တင်ပြီး Review ပေးနိုင်ပါတယ်။"

    keyboard = [
        ["⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
        ["🛒 Bot မှာယူရန်", "🔙 နောက်ပြန်ဆုပ်ရန်"]
    ]
    await update.message.reply_text(review_text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def save_review_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_review_action(update, "⭐⭐⭐")

async def save_review_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_review_action(update, "⭐⭐⭐⭐")

async def save_review_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_review_action(update, "⭐⭐⭐⭐⭐")

async def save_review_action(update: Update, rating: str):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    current_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reviews (user_id, username, rating, created_date) VALUES (?, ?, ?, ?)", (user.id, username, rating, current_date))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"ကျေးဇူးတင်ပါတယ်! သင့်ရဲ့ {rating} Review ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။ 🙏", reply_markup=get_main_menu())


# ==========================================================
# ORDER CONVERSATION
# ==========================================================

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"] = {}
    keyboard = [
        ["🤖 Starter Package", "🤖 Standard Package"],
        ["🤖 Premium Package (Customize Bot)"],
        ["❌ Order ပယ်ဖျက်ရန်"]
    ]
    await update.message.reply_text(
        "🛒 **Bot မှာယူရန် Package ရွေးချယ်ပါ**\n\n"
        "✨ *မှာယူရာတွင် ငွေကြိုရှင်းရန် မလိုပါ။ Bot ပြီးစီး၍ စမ်းသပ်ပြီးမှသာ ငွေချေပါ။*\n"
        "(အချိန်မရွေး '❌ Order ပယ်ဖျက်ရန်' ကိုနှိပ်၍ ပယ်ဖျက်နိုင်ပါသည်)",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return PACKAGE_TYPE

async def set_package_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🛒 Bot မှာယူရန်":
        keyboard = [
            ["🤖 Starter Package", "🤖 Standard Package"],
            ["🤖 Premium Package (Customize Bot)"],
            ["❌ Order ပယ်ဖျက်ရန်"]
        ]
        await update.message.reply_text(
            "⚠️ ကျေးဇူးပြု၍ အောက်ပါ Package များထဲမှ တစ်ခုကို ရွေးချယ်ပေးပါခင်ဗျာ 👇",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return PACKAGE_TYPE

    if "Starter" in text:
        package_name = "Starter Package"
    elif "Standard" in text:
        package_name = "Standard Package"
    elif "Premium" in text:
        package_name = "Premium Package"
    else:
        package_name = text

    context.user_data["order"]["package"] = package_name

    keyboard = [
        ["🛒 Shop Bot", "🎮 Game Top-up Bot"],
        ["🤖 AI Chat Bot", "📢 Channel Bot"],
        ["🏢 Business Bot", "✍️ Custom Bot"],
        ["❌ Order ပယ်ဖျက်ရန်"]
    ]
    await update.message.reply_text(
        f"✅ **ရွေးချယ်ထားသော Package:** `{package_name}`\n\n"
        "🤖 ဆက်လက်၍ မည်သည့် Bot အမျိုးအစား (Bot Type) ရေးဆွဲလိုသလဲ ရွေးချယ်ပေးပါခင်ဗျာ 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return BOT_TYPE

async def set_bot_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🛒 Bot မှာယူရန်":
        keyboard = [
            ["🛒 Shop Bot", "🎮 Game Top-up Bot"],
            ["🤖 AI Chat Bot", "📢 Channel Bot"],
            ["🏢 Business Bot", "✍️ Custom Bot"],
            ["❌ Order ပယ်ဖျက်ရန်"]
        ]
        await update.message.reply_text(
            "⚠️ ကျေးဇူးပြု၍ အောက်ပါ Bot အမျိုးအစားများထဲမှ တစ်ခုကို ရွေးချယ်ပေးပါခင်ဗျာ 👇",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return BOT_TYPE

    context.user_data["order"]["bot_type"] = text

    # 💡 ဖြည့်စွက်ချက်: စာမရိုက်ဘဲ ကျော်နိုင်ရန် Button ထည့်သွင်းပေးထားပါသည်
    keyboard = [
        ["⚙️ Function များ တိုက်ရိုက်ရွေးချယ်မည် ➡️"],
        ["❌ Order ပယ်ဖျက်ရန်"]
    ]
    await update.message.reply_text(
        f"✅ **ရွေးချယ်ထားသော Bot Type:** `{text}`\n\n"
        "📝 သင်လိုချင်သော Bot Idea နှင့် အချက်အလက်များကို စာဖြင့် ရေးသားပေးနိုင်ပါသည်။\n"
        "(ဥပမာ - Game ID လက်ခံပြီး Screenshot အော်ဒါယူပေးသော Bot)\n\n"
        "💡 *စာမရေးလိုပါက အောက်ပါ **'⚙️ Function များ တိုက်ရိုက်ရွေးချယ်မည် ➡️'** ခလုတ်ကို နှိပ်၍ ကျော်သွားနိုင်ပါသည်၊၊*",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return DESCRIPTION

async def set_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # 💡 စာမရိုက်ဘဲ Skip ခလုတ်နှိပ်ပါက Automatic အလိုအလျောက် သတ်မှတ်ပေးခြင်း
    if text == "⚙️ Function များ တိုက်ရိုက်ရွေးချယ်မည် ➡️":
        context.user_data["order"]["description"] = "သတ်မှတ်ချက်မရှိပါ (Function အလိုက် ရေးဆွဲပေးပါ)"
    else:
        context.user_data["order"]["description"] = text

    context.user_data["order"]["selected_features"] = []

    keyboard = [
        ["Auto Reply", "Payment System"],
        ["Database", "Admin Panel"],
        ["User Management", "AI Function"],
        ["➡️ ပြီးပါပြီ (Next)", "❌ Order ပယ်ဖျက်ရန်"]
    ]
    await update.message.reply_text(
        "⚙️ **လိုအပ်သော Function များကို ရွေးချယ်ပါ (တစ်ခုထက်ပို၍ ရွေးချယ်နိုင်ပါသည်):**\n\n"
        "လိုချင်သော Function များကို ခလုတ်များ နှိပ်၍ သို့မဟုတ် စာဖြင့် ရိုက်ပို့ပါ။\n"
        "ရွေးချယ်မှု ပြီးစီးပါက **'➡️ ပြီးပါပြီ (Next)'** ကို နှိပ်ပါခင်ဗျာ။",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return FEATURES

async def set_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    selected = context.user_data["order"].get("selected_features", [])

    if text == "➡️ ပြီးပါပြီ (Next)":
        if not selected:
            await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ အနည်းဆုံး Function တစ်ခု ရွေးချယ်ပါ သို့မဟုတ် စာဖြင့် ရိုက်ပို့ပေးပါ။")
            return FEATURES
        
        context.user_data["order"]["features"] = ", ".join(selected)
        
        keyboard = [["❌ Order ပယ်ဖျက်ရန်"]]
        await update.message.reply_text(
            "👤 သင့်အမည်၊ Phone Number နှင့် Business Type ကို ရေးပေးပါ။\n\n"
            "ဥပမာ - Aung, 09123456789, Online Shop",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return CUSTOMER_INFO

    clean_text = text.replace("✅", "").strip()
    if clean_text in selected:
        selected.remove(clean_text)
        msg_status = f"❌ '{clean_text}' ကို ပြန်ဖြုတ်လိုက်ပါသည်။"
    else:
        selected.append(clean_text)
        msg_status = f"✅ '{clean_text}' ကို ထည့်သွင်းလိုက်ပါပြီ။"

    context.user_data["order"]["selected_features"] = selected
    current_list_str = "\n".join([f"• {item}" for item in selected]) if selected else "မရှိသေးပါ"

    keyboard = [
        ["Auto Reply", "Payment System"],
        ["Database", "Admin Panel"],
        ["User Management", "AI Function"],
        ["➡️ ပြီးပါပြီ (Next)", "❌ Order ပယ်ဖျက်ရန်"]
    ]

    await update.message.reply_text(
        f"{msg_status}\n\n"
        f"📌 **လက်ရှိ ရွေးချယ်ထားသော Function များ:**\n{current_list_str}\n\n"
        f"ထပ်မံ ရွေးချယ်ပါ သို့မဟုတ် ပြီးပါက **'➡️ ပြီးပါပြီ (Next)'** ကို နှိပ်ပါခင်ဗျာ။",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return FEATURES

async def set_customer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["customer_info"] = update.message.text
    keyboard = [
        ["💵 50,000 - 150,000 MMK", "💵 150,000 - 300,000 MMK"],
        ["💵 300,000+ MMK", "❓ Consultation လိုအပ်ပါတယ်"],
        ["❌ Order ပယ်ဖျက်ရန်"]
    ]
    await update.message.reply_text(
        "💰 သင့် Budget Range ကို ရွေးချယ်ပါ",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return BUDGET

async def set_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_data = context.user_data["order"]
    order_data["budget"] = update.message.text
    user = update.message.from_user
    username = f"@{user.username}" if user.username else "No Username"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO orders
        (user_id, name, username, customer_info, bot_type, description, features, budget, status, created_date, updated_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user.id, user.first_name, username,
            order_data["customer_info"], order_data["bot_type"],
            order_data["description"], order_data["features"],
            order_data["budget"], "Pending 🟡",
            current_date, current_date
        )
    )
    order_number = cursor.lastrowid
    order_id = f"MMB-{datetime.now().strftime('%Y%m%d')}-{order_number:04d}"
    cursor.execute("UPDATE orders SET order_id = ? WHERE id = ?", (order_id, order_number))
    conn.commit()
    conn.close()

    summary = (
        "✅ **Order တင်ခြင်း အောင်မြင်ပါပြီ**\n\n"
        f"📌 Order ID: `{order_id}`\n"
        f"📦 Package: `{order_data.get('package', 'Starter Package')}`\n"
        f"🤖 Bot Type: `{order_data.get('bot_type', 'N/A')}`\n"
        f"📝 Description: {order_data['description']}\n"
        f"⚙️ Features: {order_data['features']}\n"
        f"💰 Budget: {order_data['budget']}\n\n"
        "✨ **မှတ်ချက်:** ငွေကြိုပေးရန် မလိုပါ။ Bot ရေးဆွဲပြီးစီး၍ စမ်းသပ်ပြီးမှသာ ငွေပေးချေရမည် ဖြစ်ပါသည်။\n\n"
        "Developer မှ စစ်ဆေးပြီး မကြာမီ ဆက်သွယ်ပေးပါမည်။ 🙏"
    )
    
    review_keyboard = [
        ["⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
        ["🏠 ပင်မမီနူးသို့ ပြန်ရန်"]
    ]
    await update.message.reply_text(summary, reply_markup=ReplyKeyboardMarkup(review_keyboard, resize_keyboard=True), parse_mode="Markdown")

    admin_text = (
        "📩 **NEW BOT ORDER**\n\n"
        f"📌 Order ID: `{order_id}`\n"
        f"👤 Customer: {user.first_name}\n"
        f"📱 Username: {username}\n"
        f"🆔 User ID: `{user.id}`\n\n"
        f"📦 Package: {order_data.get('package', 'Starter Package')}\n"
        f"🤖 Bot Type: {order_data.get('bot_type', 'N/A')}\n"
        f"📝 Idea: {order_data['description']}\n"
        f"⚙️ Feature: {order_data['features']}\n"
        f"💰 Budget: {order_data['budget']}\n\n"
        f"📅 Date: {current_date}"
    )

    admin_inline_keyboard = [
        [
            InlineKeyboardButton("🟢 Accept", callback_data=f"status_accept_{order_id}"),
            InlineKeyboardButton("🟡 In Progress", callback_data=f"status_progress_{order_id}")
        ],
        [
            InlineKeyboardButton("✅ Completed", callback_data=f"status_complete_{order_id}"),
            InlineKeyboardButton("🔴 Cancel", callback_data=f"status_cancel_{order_id}")
        ]
    ]

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            reply_markup=InlineKeyboardMarkup(admin_inline_keyboard),
            parse_mode="Markdown"
        )
    except Exception as error:
        logging.error(f"Admin notification failed: {error}")

    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Order တင်ခြင်းကို ပယ်ဖျက်လိုက်ပါပြီ။", reply_markup=get_main_menu())
    return ConversationHandler.END


# ==========================================================
# ADMIN COMMANDS
# ==========================================================

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ ဒီ Command ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status LIKE '%Pending%'")
    pending_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status LIKE '%Progress%'")
    progress_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status LIKE '%Completed%'")
    completed_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status LIKE '%Cancelled%'")
    cancelled_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]
    conn.close()

    stats_msg = (
        "📊 **MM Bot Market Dashboard & Analytics**\n\n"
        f"👥 **စုစုပေါင်း အသုံးပြုသူ (Users):** {total_users} ယောက်\n"
        f"📦 **စုစုပေါင်း အော်ဒါ (Total Orders):** {total_orders} ခု\n"
        "-----------------------------------\n"
        f"🟡 **စောင့်ဆိုင်းဆဲ (Pending):** {pending_orders} ခု\n"
        f"⚙️ **ရေးဆွဲနေဆဲ (In Progress):** {progress_orders} ခု\n"
        f"✅ **ပြီးစီးပြီး (Completed):** {completed_orders} ခု\n"
        f"🔴 **ပယ်ဖျက်လိုက်သော (Cancelled):** {cancelled_orders} ခု\n"
        "-----------------------------------\n"
        f"⭐ **စုစုပေါင်း သုံးသပ်ချက်များ (Reviews):** {total_reviews} ခု"
    )
    await update.message.reply_text(stats_msg, parse_mode="Markdown")

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ ဒီ Command ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, order_id, user_id, name, username, customer_info, bot_type, description, features, budget, status, created_date, updated_date FROM orders")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("⚠️ ထုတ်ယူရန် Order စာရင်း ဒေတာ မရှိသေးပါ။")
        return

    filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow([
            "ID", "Order ID", "User ID", "Name", "Username", 
            "Customer Info", "Bot Type", "Description", "Features", 
            "Budget", "Status", "Created Date", "Updated Date"
        ])
        writer.writerows(rows)

    try:
        with open(filename, "rb") as doc:
            await context.bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=doc,
                filename=filename,
                caption=f"📊 **MM Bot Market - Order Data Export**\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="Markdown"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ File ပို့ရာတွင် အမှားအယွင်း ရှိပါသည်: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ ဒီ Command ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ စာသား ထည့်သွင်းပေးပါ။\n\n"
            "ဥပမာ - `/broadcast မင်္ဂလာပါ၊ MM Bot Market မှ Promotion အသစ်များ ရရှိနိုင်ပါပြီ။`",
            parse_mode="Markdown"
        )
        return

    broadcast_msg = " ".join(context.args)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    success_count = 0
    fail_count = 0

    await update.message.reply_text(f"📢 Broadcast ပို့ခြင်း စတင်နေပါပြီ... (စုစုပေါင်း User {len(users)} ယောက်)")

    for user_row in users:
        user_id = user_row[0]
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 **MM Bot Market မှ အသိပေးချက်**\n\n{broadcast_msg}",
                parse_mode="Markdown"
            )
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail_count += 1

    await update.message.reply_text(
        f"✅ **Broadcast ပို့ဆောင်မှု ပြီးစီးပါပြီ**\n\n"
        f"🟢 အောင်မြင်စွာ ရောက်ရှိ: {success_count}\n"
        f"🔴 မရောက်ရှိပါ/Blocked: {fail_count}"
    )


# ==========================================================
# ADMIN INTERACTIVE STATUS CALLBACK
# ==========================================================

async def admin_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split("_")
    action = parts[1]
    order_id = "_".join(parts[2:])

    status_map = {
        "accept": "Accepted 🟢 (စတင်လက်ခံထားသည်)",
        "progress": "In Progress 🟡 (ရေးဆွဲနေသည်)",
        "complete": "Completed ✅ (ပြီးစီးပါပြီ)",
        "cancel": "Cancelled 🔴 (ပယ်ဖျက်လိုက်သည်)"
    }

    new_status = status_map.get(action, "Updated 🔵")
    updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM orders WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()

    if order:
        user_id = order[0]
        cursor.execute("UPDATE orders SET status = ?, updated_date = ? WHERE order_id = ?", (new_status, updated_date, order_id))
        conn.commit()

        try:
            user_msg = (
                f"🔔 **Order Status အသစ်**\n\n"
                f"📌 Order ID: `{order_id}`\n"
                f"📊 Status: **{new_status}**\n"
                f"🕒 Update ပြုလုပ်ချိန်: {updated_date}\n\n"
                f"ကျေးဇူးတင်ရှိပါသည်။ 🙏"
            )
            await context.bot.send_message(chat_id=user_id, text=user_msg, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Failed to send customer notification: {e}")

        original_text = query.message.text
        new_admin_text = f"{original_text}\n\n-------------------\n🔄 **Current Status:** {new_status}\n🕒 {updated_date}"
        await query.edit_message_text(
            text=new_admin_text,
            reply_markup=query.message.reply_markup,
            parse_mode="Markdown"
        )
    conn.close()


# ==========================================================
# AUTOMATIC ERROR ALERT SYSTEM
# ==========================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    error_message = (
        "🚨 **AUTOMATIC SYSTEM ERROR ALERT**\n\n"
        f"An exception was raised while handling an update:\n"
        f"```python\n{html.escape(tb_string[-3000:])}\n```"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=error_message,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Failed to send error alert to Admin: {e}")


# ==========================================================
# PAGINATED MY ORDER STATUS SYSTEM
# ==========================================================

def get_order_status_page(user_id: int, page: int = 1, items_per_page: int = 5):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,))
    total_orders = cursor.fetchone()[0]

    if total_orders == 0:
        conn.close()
        return "⚠️ **သင့်တွင် တင်ထားသော အော်ဒါ မရှိသေးပါခင်ဗျာ။**\n\nBot မှာယူလိုပါက '🛒 Bot မှာယူရန်' ခလုတ်ကို နှိပ်၍ မှာယူနိုင်ပါသည်။", None

    total_pages = (total_orders + items_per_page - 1) // items_per_page
    offset = (page - 1) * items_per_page

    cursor.execute(
        "SELECT order_id, bot_type, status, updated_date FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
        (user_id, items_per_page, offset)
    )
    orders = cursor.fetchall()
    conn.close()

    text = f"📦 **သင့်၏ အော်ဒါများ အခြေအနေ (My Order Status)** [Page {page}/{total_pages}]\n\n"
    for o in orders:
        order_id, bot_type, status, updated_date = o
        text += (
            f"📌 **Order ID:** `{order_id}`\n"
            f"🤖 **Bot Type:** `{bot_type}`\n"
            f"📊 **Status:** {status}\n"
            f"🕒 **နောက်ဆုံးပြင်ဆင်ချိန်:** {updated_date}\n"
            f"-----------------------------------\n"
        )

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ ယခင်", callback_data=f"orderpage_{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("နောက်တစ်ခု ➡️", callback_data=f"orderpage_{page+1}"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
    return text, reply_markup

async def show_my_order_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text, reply_markup = get_order_status_page(user_id, page=1)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def order_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = int(query.data.split("_")[1])
    user_id = query.from_user.id

    text, reply_markup = get_order_status_page(user_id, page=page)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error updating order status page: {e}")


# ==========================================================
# BACK TO MAIN MENU ROUTE
# ==========================================================

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=get_main_menu())


# ==========================================================
# MAIN DISPATCHER
# ==========================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # 1. ORDER CONVERSATION
    order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🛒 Bot မှာယူရန်$"), start_order)],
        states={
            PACKAGE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔙 နောက်ပြန်ဆုပ်ရန်|❌ Order ပယ်ဖျက်ရန်)$"), set_package_type)],
            BOT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔙 နောက်ပြန်ဆုပ်ရန်|❌ Order ပယ်ဖျက်ရန်)$"), set_bot_type)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔙 နောက်ပြန်ဆုပ်ရန်|❌ Order ပယ်ဖျက်ရန်)$"), set_description)],
            FEATURES: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔙 နောက်ပြန်ဆုပ်ရန်|❌ Order ပယ်ဖျက်ရန်)$"), set_features)],
            CUSTOMER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔙 နောက်ပြန်ဆုပ်ရန်|❌ Order ပယ်ဖျက်ရန်)$"), set_customer_info)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔙 နောက်ပြန်ဆုပ်ရန်|❌ Order ပယ်ဖျက်ရန်)$"), set_budget)]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^(🔙 နောက်ပြန်ဆုပ်ရန်|❌ Order ပယ်ဖျက်ရန်)$"), cancel_order),
            CommandHandler("cancel", cancel_order)
        ]
    )

    app.add_handler(order_handler)

    # 2. AUTO FETCH ORDER STATUS & PAGINATION HANDLERS
    app.add_handler(MessageHandler(filters.Regex("^📦 My Order Status$"), show_my_order_status))
    app.add_handler(CallbackQueryHandler(order_page_callback, pattern="^orderpage_"))

    # Base Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("export", export_command))

    # Service Buttons
    app.add_handler(MessageHandler(filters.Regex("^🤖 ဝန်ဆောင်မှုများ$"), show_services))
    app.add_handler(MessageHandler(filters.Regex("^🤖 Telegram Shop Bot$"), service_shop_bot))
    app.add_handler(MessageHandler(filters.Regex("^🎮 Game Top-up Bot$"), service_game_bot))
    app.add_handler(MessageHandler(filters.Regex("^📢 Channel Management Bot$"), service_channel_bot))
    app.add_handler(MessageHandler(filters.Regex("^🤖 AI Chat Bot$"), service_ai_bot))
    app.add_handler(MessageHandler(filters.Regex("^🏢 Business Automation Bot$"), service_business_bot))
    app.add_handler(MessageHandler(filters.Regex("^⚙️ Custom Telegram Bot$"), service_custom_bot))

    # Pricing Views
    app.add_handler(MessageHandler(filters.Regex("^💰🤖 ဈေးနှုန်းများ$"), show_pricing))
    app.add_handler(MessageHandler(filters.Regex("^🤖 Starter Package$"), view_starter_package))
    app.add_handler(MessageHandler(filters.Regex("^🤖 Standard Package$"), view_standard_package))
    app.add_handler(MessageHandler(filters.Regex("^🤖 Premium Package \\(Customize Bot\\)$"), view_premium_package))

    # Direct Redirects
    app.add_handler(MessageHandler(filters.Regex("^🎬 Demo Bot စမ်းသုံးကြည့်ရန်$"), demo_redirect))
    app.add_handler(MessageHandler(filters.Regex("^🧑‍💻 Developer \\(စောက်ချောကြီး\\) နှင့် ဆွေးနွေးရန်$"), developer_contact))
    app.add_handler(MessageHandler(filters.Regex("^🚨 🤖 Customize Bot အတွက် Developer.*"), developer_contact))

    # FAQ & Reviews
    app.add_handler(MessageHandler(filters.Regex("^❓ FAQ$"), show_faq))
    app.add_handler(MessageHandler(filters.Regex("^⭐ Customer Review$"), show_reviews))
    app.add_handler(MessageHandler(filters.Regex("^⭐⭐⭐$"), save_review_3))
    app.add_handler(MessageHandler(filters.Regex("^⭐⭐⭐⭐$"), save_review_4))
    app.add_handler(MessageHandler(filters.Regex("^⭐⭐⭐⭐⭐$"), save_review_5))

    # Navigation
    app.add_handler(MessageHandler(filters.Regex("^🏠 ပင်မမီနူးသို့ ပြန်ရန်$"), back_to_main))
    app.add_handler(MessageHandler(filters.Regex("^🔙 နောက်ပြန်ဆုပ်ရန်$"), back_to_main))

    # Admin Callback Handler
    app.add_handler(CallbackQueryHandler(admin_status_callback, pattern="^status_"))

    # Global Error Handler
    app.add_error_handler(error_handler)

    print("MM Bot Market Enterprise Engine Started Successfully...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
