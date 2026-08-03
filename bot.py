import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

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

# ---------------------------------------------------------
# Admin Chat ID နှင့် Developer Username ပြင်ဆင်ပြီး
ADMIN_CHAT_ID = "8582190375"  
DEVELOPER_USERNAME = "superraizo7"
# ---------------------------------------------------------

# Conversation States
BOT_TYPE, DESCRIPTION, FEATURES, CUSTOMER_INFO, BUDGET = range(5)
ORDER_SEARCH = 5

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
                    phone TEXT,
                    business_type TEXT,
                    bot_type TEXT,
                    description TEXT,
                    features TEXT,
                    budget TEXT,
                    status TEXT,
                    date TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# Main Menu Keyboard
def get_main_menu():
    keyboard = [
        ["🤖 ဝန်ဆောင်မှုများ", "💰 စျေးနှုန်းများ"],
        ["🎬 Demo / Portfolio", "🛒 Bot မှာယူရန်"],
        ["⭐ Customer Review", "❓ FAQ"],
        ["📦 My Order Status", "👨‍💻 Developer နှင့် ဆွေးနွေးရန်"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------------- COMMANDS & HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 **MM Bot Market မှ ကြိုဆိုပါတယ်**\n\n"
        "သင့် Business အတွက် Professional Telegram Bot များကို စိတ်ကြိုက်ဖန်တီးပေးပါတယ်။\n\n"
        "ကျွန်ုပ်တို့ ဖန်တီးပေးနိုင်သော Bot များ👇\n"
        "🛒 Online Shop Bot\n"
        "🎮 Game Top-up Bot\n"
        "📢 Telegram Channel Bot\n"
        "🤖 AI Chat Bot\n"
        "🏢 Business Automation Bot\n"
        "✍️ Custom Bot\n\n"
        "သင့်လုပ်ငန်းအတွက် သင့်တော်သော Bot Solution ကို ရွေးချယ်ပါ 👇"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛒 **Telegram Shop Bot**\nFeatures: Product Catalog, Order System, Customer Database, Admin Notification, Auto Reply\n\n"
        "🎮 **Game Top-up Bot**\nFeatures: Customer Order Form, Player Info Collection, Payment Confirmation, Order Management, Admin Control\n\n"
        "📢 **Channel Management Bot**\nFeatures: Auto Post, Auto Reply, Member Verification, Channel Automation\n\n"
        "🤖 **AI Chat Bot**\nFeatures: AI Assistant, Customer Support, Automatic Reply, FAQ System\n\n"
        "🏢 **Business Automation Bot**\nFeatures: Booking System, Customer Database, Workflow Automation, Business Management\n\n"
        "✍️ **Custom Bot**\nFeatures: Fully Customized Development, Custom Functions, Unique Business Solutions\n\n"
        "-------------------------------\n"
        "သင်လိုချင်သော Bot ရှိပါက **🛒 Bot မှာယူရန်** ကိုနှိပ်ပြီး Order တင်နိုင်ပါတယ်။"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def show_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💰 **Bot Development Price**\n\n"
        "🥉 **Basic Bot**: 50,000 MMK - 100,000 MMK\n"
        "🥈 **Medium Bot**: 100,000 MMK - 300,000 MMK\n"
        "🥇 **Advanced Bot**: 300,000 MMK +\n\n"
        "💡 *Note: Final price depends on Features, Design, Database, and Complexity.*"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def show_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎬 **Demo / Portfolio**\n\n"
        "🤖 Shop Bot Demo\n"
        "🎮 Game Top-up Bot Demo\n"
        "📢 Channel Management Bot Demo\n"
        "🧠 AI Bot Demo\n"
        "🏢 Business Automation Demo\n\n"
        "Demo များနှင့် အသေးစိတ်အချက်အလက်များကို ကြည့်ရှုနိုင်ပါတယ်။"
    )
    await update.message.reply_text(text)

async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⭐ **Customer Reviews**\n\n"
        "⭐⭐⭐⭐⭐\n\"Professional Bot Service\"\n\n"
        "⭐⭐⭐⭐⭐\n\"Fast Delivery & Good Support\"\n\n"
        "⭐⭐⭐⭐⭐\n\"စျေးနှုန်း သက်သာပြီး စိတ်တိုင်းကျပါတယ်\""
    )
    await update.message.reply_text(text)

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ **Frequently Asked Questions (FAQ)**\n\n"
        "Q: Bot ဖန်တီးဖို့ ဘယ်လောက်ကြာပါသလဲ?\n"
        "A: ပုံမှန်အားဖြင့် Bot Complexity ပေါ်မူတည်ပြီး ၃ ရက်မှ ၁၄ ရက်အထိ ကြာနိုင်ပါတယ်။\n\n"
        "Q: ရှိပြီးသား Bot ကို ပြင်ဆင်နိုင်ပါသလား?\n"
        "A: ရပါတယ်။ Existing Bot များကို Update နှင့် Modify ပြုလုပ်ပေးနိုင်ပါတယ်။\n\n"
        "Q: Support ရပါသလား?\n"
        "A: ရပါတယ်။ Delivery ပြီးနောက် Basic Support ပေးပါမည်။"
    )
    await update.message.reply_text(text)

async def developer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("👨‍💻 Developer ထံ တိုက်ရိုက်ဆက်သွယ်ရန်", url=f"https://t.me/{DEVELOPER_USERNAME}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Developer နှင့် တိုက်ရိုက် ဆွေးနွေးလိုပါက အောက်ပါ Button ကို နှိပ်ပါ -", reply_markup=reply_markup)

# ---------------- ORDER CONVERSATION FLOW ----------------

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order'] = {}
    keyboard = [
        ["🛒 Shop Bot", "🎮 Game Top-up Bot"],
        ["🤖 AI Chat Bot", "📢 Channel Bot"],
        ["🏢 Business Bot", "✍️ Custom Bot"]
    ]
    await update.message.reply_text(
        "🤖 **သင်ဖန်တီးလိုသော Bot အမျိုးအစားကို ရွေးချယ်ပါ**",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return BOT_TYPE

async def set_bot_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['bot_type'] = update.message.text
    await update.message.reply_text("📝 **သင်လိုချင်သော Bot Idea နှင့် Feature များကို အသေးစိတ်ရေးပေးပါ။**")
    return DESCRIPTION

async def set_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['description'] = update.message.text
    keyboard = [
        ["✅ Auto Reply", "✅ Payment System"],
        ["✅ Database", "✅ Admin Panel"],
        ["✅ User Management", "✅ AI Function"]
    ]
    await update.message.reply_text(
        "⚙️ **လိုအပ်သော Function များကို ရွေးချယ်ပါ သို့မဟုတ် စာဖြင့် ရေးပို့ပါ**",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return FEATURES

async def set_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['features'] = update.message.text
    await update.message.reply_text("👤 **သင့်အမည်၊ Phone Number နှင့် Business Type တိုကို ရေးသားပေးပါ**\n(ဥပမာ - ဦးအောင်၊ 09123456789၊ Online Shop)")
    return CUSTOMER_INFO

async def set_customer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order']['customer_info'] = update.message.text
    keyboard = [
        ["💵 50,000 MMK အောက်", "💵 50,000 - 200,000 MMK"],
        ["💵 200,000 MMK အထက်", "❓ Consultation လိုအပ်ပါတယ်"]
    ]
    await update.message.reply_text(
        "💰 **သင့်၏ Budget Range ကို ရွေးချယ်ပါ**",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return BUDGET

async def set_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_data = context.user_data['order']
    order_data['budget'] = update.message.text
    user = update.message.from_user

    # Generate Order ID and save to Database
    conn = sqlite3.connect('mm_bot_market.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders")
    count = c.fetchone()[0] + 1
    order_id = f"MMB-{count:04d}"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute('''INSERT INTO orders (order_id, user_id, name, username, phone, business_type, bot_type, description, features, budget, status, date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (order_id, user.id, user.first_name, f"@{user.username}", order_data['customer_info'], "",
               order_data['bot_type'], order_data['description'], order_data['features'], order_data['budget'], 'Pending 🟡', current_date))
    conn.commit()
    conn.close()

    # Customer Summary Message
    summary = (
        f"✅ **Order တင်ခြင်း အောင်မြင်ပါပြီ**\n\n"
        f"📌 **Order ID:** `{order_id}`\n"
        f"🤖 **Bot Type:** {order_data['bot_type']}\n"
        f"📝 **Description:** {order_data['description']}\n"
        f"⚙️ **Features:** {order_data['features']}\n"
        f"💰 **Budget:** {order_data['budget']}\n\n"
        f"Developer မှ စစ်ဆေးပြီး မကြာမီ ပြန်လည် ဆက်သွယ်ပေးပါမည်။"
    )
    await update.message.reply_text(summary, reply_markup=get_main_menu(), parse_mode='Markdown')

    # Admin Alert Notification
    admin_alert = (
        f"📩 **NEW BOT ORDER RECEIVED**\n\n"
        f"📌 **Order ID:** `{order_id}`\n"
        f"👤 **Customer:** {user.first_name}\n"
        f"📱 **Username:** @{user.username}\n"
        f"☎️ **Info:** {order_data['customer_info']}\n"
        f"🤖 **Bot Type:** {order_data['bot_type']}\n"
        f"📝 **Idea:** {order_data['description']}\n"
        f"⚙️ **Features:** {order_data['features']}\n"
        f"💰 **Budget:** {order_data['budget']}\n"
        f"📅 **Date:** {current_date}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_alert, parse_mode='Markdown')
    except Exception as e:
        print(f"Failed to alert admin: {e}")

    return ConversationHandler.END

# ---------------- ORDER STATUS TRACKING ----------------

async def request_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 စစ်ဆေးလိုသော **Order ID** ကို ရိုက်ထည့်ပေးပါ (ဥပမာ - MMB-0001):")
    return ORDER_SEARCH

async def check_order_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_id = update.message.text.strip().upper()
    conn = sqlite3.connect('mm_bot_market.db')
    c = conn.cursor()
    c.execute("SELECT order_id, status, date FROM orders WHERE order_id = ?", (input_id,))
    res = c.fetchone()
    conn.close()

    if res:
        response = (
            f"📌 **Order ID:** `{res[0]}`\n"
            f"📊 **Current Status:** {res[1]}\n"
            f"📅 **Last Update:** {res[2]}\n\n"
            f"💳 **Payment Info:** KBZ Pay / Wave Money အကောင့်များအတွက် Developer ထံ တိုက်ရိုက် မေးမြန်းနိုင်ပါသည်။"
        )
    else:
        response = "❌ Order ID မတွေ့ရှိပါ။ ကျေးဇူးပြု၍ Order ID မှန်ကန်စွာ ပြန်လည် ထည့်သွင်းပေးပါ။"

    await update.message.reply_text(response, reply_markup=get_main_menu(), parse_mode='Markdown')
    return ConversationHandler.END

# ---------------- MAIN DISPATCHER ----------------

def main():
    # Telegram Bot Token ပြင်ဆင်ပြီး
    app = Application.builder().token("8912157146:AAGBD4IVht73iJS5quj5YpPNH-").build()  # သင့် Bot Token ထည့်ပါ

    order_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🛒 Bot မှာယူရန်$'), start_order)],
        states={
            BOT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_bot_type)],
            DESCRIPTION: [MessageHandler(filtPHISfFQpQers.TEXT & ~filters.COMMAND, set_description)],
            FEATURES: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_features)],
            CUSTOMER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_customer_info)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_budget)]
        },
        fallbacks=[]
    )

    status_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📦 My Order Status$'), request_order_id)],
        states={
            ORDER_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_order_status)]
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex('^🤖 ဝန်ဆောင်မှုများ$'), show_services))
    app.add_handler(MessageHandler(filters.Regex('^💰 စျေးနှုန်းများ$'), show_pricing))
    app.add_handler(MessageHandler(filters.Regex('^🎬 Demo / Portfolio$'), show_portfolio))
    app.add_handler(MessageHandler(filters.Regex('^⭐ Customer Review$'), show_reviews))
    app.add_handler(MessageHandler(filters.Regex('^❓ FAQ$'), show_faq))
    app.add_handler(MessageHandler(filters.Regex('^👨‍💻 Developer နှင့် ဆွေးနွေးရန်$'), developer_contact))
    
    app.add_handler(order_conv)
    app.add_handler(status_conv)

    print("MM Bot Market System Started...")
    app.run_polling()

if __name__ == '__main__':
    main()
