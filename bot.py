import os
import csv
import html
import time
import logging
import asyncio
import aiosqlite
import threading
import traceback
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
    TypeHandler,
    ApplicationHandlerStop
)

# ==========================================================
# LOGGING & CONFIG
# ==========================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8582190375"))
DEVELOPER_USERNAME = "superraizo7"
DEMO_BOT_USERNAME = "OnlineshopDemo88_bot"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

DB_NAME = "mm_bot_market.db"

# ==========================================================
# KEEP ALIVE SERVER
# ==========================================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MM Bot Market Enterprise Active!")
    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ==========================================================
# ASYNC DATABASE (aiosqlite)
# ==========================================================
async def init_db(app: Application):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                phone TEXT DEFAULT NULL,
                business_type TEXT DEFAULT NULL,
                joined_date TEXT,
                is_banned INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
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
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                rating TEXT,
                created_date TEXT
            )
        """)
        await db.commit()
        
        # Load Banned Users into memory
        async with db.execute("SELECT user_id FROM users WHERE is_banned = 1") as cursor:
            async for row in cursor:
                BANNED_USERS.add(row[0])

# ==========================================================
# SECURITY: ANTI-SPAM, RATE LIMIT & AUTO-BAN
# ==========================================================
USER_ACTIVITY = {}
BANNED_USERS = set()

async def security_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    # 1. Ban Check
    if user.id in BANNED_USERS:
        raise ApplicationHandlerStop()

    # Skip Admin
    if user.id == ADMIN_CHAT_ID:
        return

    now = time.time()
    user_data = USER_ACTIVITY.get(user.id, {"last_msg": 0, "spam_count": 0, "window_start": now})

    # 2. Rate Limiting (1.5 Seconds)
    if now - user_data["last_msg"] < 1.5:
        user_data["spam_count"] += 1
        
        if user_data["spam_count"] == 3:
            try:
                await update.effective_message.reply_text("⚠️ **Rate Limit:** ကျေးဇူးပြု၍ ဖြည်းဖြည်းသာ အသုံးပြုပါ။ (1.5s Cooldown)")
            except: pass
            
        # 3. Auto Ban (DDoS / Flood Protection)
        elif user_data["spam_count"] >= 6:
            BANNED_USERS.add(user.id)
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user.id,))
                await db.commit()
            try:
                await update.effective_message.reply_text("🚫 **BANNED:** အကြိမ်များစွာ ဆက်တိုက်ပို့ခြင်း (Spam) ပြုလုပ်မှုကြောင့် သင့်ကို စနစ်မှ Ban လိုက်ပါပြီ။")
            except: pass
            raise ApplicationHandlerStop()
            
        USER_ACTIVITY[user.id] = user_data
        raise ApplicationHandlerStop() # Stop processing this message

    # Reset spam count if slow enough
    user_data["last_msg"] = now
    if now - user_data["window_start"] > 10:
        user_data["spam_count"] = 0
        user_data["window_start"] = now
        
    USER_ACTIVITY[user.id] = user_data

# ==========================================================
# REUSABLE TEXTS
# ==========================================================
PAYMENT_POLICY_TEXT = (
    "✨ **ငွေပေးချေမှု ပေါ်လစီ (Payment Policy)**\n\n"
    "• **စရံငွေ ၅၀%** — အော်ဒါစတင်ချိန်တွင် ပေးချေရန်\n"
    "• **ကျန် ၅၀%** — Bot စမ်းသပ်ပြီးမှ အပြီးသတ် ချေရန်\n\n"
    "🛡️ **၁၀၀% စရံငွေ ပြန်အမ်းပေးသည့် အာမခံ:**\n"
    "ရေးဆွဲပေးထားသော Function များ အလုပ်မလုပ်ပါက စရံငွေ အပြည့် ပြန်အမ်းပေးပါမည်။"
)

def get_main_menu():
    keyboard = [
        ["🤖 ဝန်ဆောင်မှုများ", "💰🤖 ဈေးနှုန်းများ"],
        ["🎬 Demo Bot စမ်းသုံးရန်", "🛒 Bot မှာယူရန်"],
        ["⭐ Customer Review", "❓ FAQ"],
        ["📦 My Order Status", "⚙️ My Profile"],
        ["👨‍💻 Tech Support နှင့် ဆွေးနွေးရန်"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==========================================================
# START & PROFILE SYSTEM
# ==========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else "No Username"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, name, username, joined_date) VALUES (?, ?, ?, ?)",
            (user.id, user.first_name, username, current_date)
        )
        await db.commit()

    text = f"🤖 **MM Bot Market မှ ကြိုဆိုပါတယ်**\n\nသင့် Business အတွက် Professional Telegram Bot များကို ဖန်တီးပေးပါတယ်။\n\n{PAYMENT_POLICY_TEXT}"
    await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")

# PROFILE STATES
PROF_PHONE, PROF_BIZ = range(10, 12)

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT phone, business_type FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            
    phone = row[0] if row and row[0] else "မဖြည့်ရသေးပါ"
    biz = row[1] if row and row[1] else "မဖြည့်ရသေးပါ"
    
    text = f"⚙️ **သင့် Profile အချက်အလက်များ**\n\n📱 ဖုန်းနံပါတ်: {phone}\n🏢 လုပ်ငန်းအမျိုးအစား: {biz}\n\nအချက်အလက်များ ဖြည့်သွင်း/ပြင်ဆင်ရန် အောက်ပါ ခလုတ်ကို နှိပ်ပါ။"
    keyboard = [[InlineKeyboardButton("✏️ Profile ပြင်ဆင်မည်", callback_data="edit_profile")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def edit_profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📱 ကျေးဇူးပြု၍ သင့် ဆက်သွယ်ရန် ဖုန်းနံပါတ်ကို ရိုက်ထည့်ပါ။", reply_markup=ReplyKeyboardRemove())
    return PROF_PHONE

async def save_prof_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['prof_phone'] = update.message.text
    await update.message.reply_text("🏢 သင့် လုပ်ငန်းအမည် သို့မဟုတ် အမျိုးအစားကို ရိုက်ထည့်ပါ။ (ဥပမာ - Online Shop, Game Shop)")
    return PROF_BIZ

async def save_prof_biz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = context.user_data.get('prof_phone')
    biz = update.message.text
    user_id = update.message.from_user.id
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET phone = ?, business_type = ? WHERE user_id = ?", (phone, biz, user_id))
        await db.commit()
        
    await update.message.reply_text("✅ Profile အချက်အလက်များ မှတ်သားပြီးပါပြီ။ Order တင်ရာတွင် ပိုမိုမြန်ဆန်ပါလိမ့်မည်။", reply_markup=get_main_menu())
    return ConversationHandler.END

# ==========================================================
# VERIFIED REVIEW SYSTEM
# ==========================================================
async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT username, rating, created_date FROM reviews ORDER BY id DESC LIMIT 5") as cursor:
            rows = await cursor.fetchall()
            
    review_text = "⭐ **Customer Reviews**\n\n"
    if rows:
        for r in rows:
            review_text += f"👤 {r[0]} | Rating: {r[1]} | 📅 {r[2]}\n"
    else:
        review_text += "✨ Review ပေးထားသူ မရှိသေးပါ။"

    keyboard = [["⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], ["🏠 ပင်မမီနူးသို့ ပြန်ရန်"]]
    await update.message.reply_text(review_text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")

async def save_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rating = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    
    # VERIFICATION: Check if user has at least one Completed Order
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM orders WHERE user_id = ? AND status LIKE '%Completed%'", (user_id,)) as cursor:
            completed_orders = (await cursor.fetchone())[0]
            
    if completed_orders == 0:
        await update.message.reply_text("⚠️ **Review ပေးရန် မဖြစ်နိုင်ပါ။**\n\nBot လက်ခံရရှိပြီး (Completed Status) ဖြစ်သော Customer များသာ Review ပေးနိုင်ပါသည်ခင်ဗျာ။", reply_markup=get_main_menu(), parse_mode="Markdown")
        return
        
    current_date = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO reviews (user_id, username, rating, created_date) VALUES (?, ?, ?, ?)", (user_id, username, rating, current_date))
        await db.commit()
        
    await update.message.reply_text(f"ကျေးဇူးတင်ပါတယ်! သင့်ရဲ့ {rating} Review ကို မှတ်တမ်းတင်ပြီးပါပြီ။ 🙏", reply_markup=get_main_menu())

# ==========================================================
# ORDER CONVERSATION (WITH CONFIRM & EDIT)
# ==========================================================
PACKAGE_TYPE, BOT_TYPE, DESCRIPTION, FEATURES, CUSTOMER_INFO, BUDGET, CONFIRMATION = range(7)

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"] = {}
    keyboard = [["🤖 Starter", "🤖 Standard"], ["🤖 Premium (Custom)"], ["❌ Cancel Order"]]
    await update.message.reply_text("🛒 **Package ရွေးချယ်ပါ**", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return PACKAGE_TYPE

async def set_package_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["package"] = update.message.text.strip()
    keyboard = [["🛒 Shop Bot", "🎮 Game Bot"], ["🤖 AI Chat", "📢 Channel"], ["🏢 Business", "✍️ Custom"], ["❌ Cancel Order"]]
    await update.message.reply_text("🤖 မည်သည့် Bot အမျိုးအစား ရေးဆွဲလိုသလဲ?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return BOT_TYPE

async def set_bot_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["bot_type"] = update.message.text.strip()
    keyboard = [["⚙️ Function တိုက်ရိုက်ရွေးမည် ➡️"], ["❌ Cancel Order"]]
    await update.message.reply_text("📝 သင့် Bot Idea ကို စာဖြင့် ရေးသားပေးပါ။", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return DESCRIPTION

async def set_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["order"]["description"] = "သတ်မှတ်ချက်မရှိပါ" if text.startswith("⚙️") else text
    context.user_data["order"]["selected_features"] = []
    
    keyboard = [["Auto Reply", "Payment System"], ["Database", "Admin Panel"], ["➡️ ပြီးပါပြီ (Next)", "❌ Cancel Order"]]
    await update.message.reply_text("⚙️ **Function များ ရွေးချယ်ပါ:**", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return FEATURES

async def set_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    selected = context.user_data["order"].get("selected_features", [])

    if text == "➡️ ပြီးပါပြီ (Next)":
        context.user_data["order"]["features"] = ", ".join(selected) if selected else "Standard"
        
        # Check Profile for pre-fill
        user_id = update.message.from_user.id
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT phone, business_type FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                
        if row and row[0] and row[1]:
            context.user_data["order"]["customer_info"] = f"{update.message.from_user.first_name}, {row[0]}, {row[1]}"
            # Skip asking info, go to budget
            keyboard = [["💵 50k - 150k", "💵 150k - 300k"], ["💵 300k+", "❓ Consultation"], ["❌ Cancel Order"]]
            await update.message.reply_text("✅ သင့် Profile အချက်အလက်ကို ယူလိုက်ပါပြီ။\n\n💰 Budget Range ရွေးပါ-", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return BUDGET
        else:
            keyboard = [["❌ Cancel Order"]]
            await update.message.reply_text("👤 သင့်အမည်၊ ဖုန်းနံပါတ် နှင့် လုပ်ငန်းအမည်ကို ရေးပေးပါ။ (ဥပမာ: Aung, 09123, Online Shop)", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return CUSTOMER_INFO

    clean_text = text.replace("✅", "").strip()
    if clean_text in selected: selected.remove(clean_text)
    else: selected.append(clean_text)
    
    context.user_data["order"]["selected_features"] = selected
    await update.message.reply_text(f"📌 ရွေးချယ်ထားသော: {', '.join(selected)}")
    return FEATURES

async def set_customer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["customer_info"] = update.message.text
    keyboard = [["💵 50k - 150k", "💵 150k - 300k"], ["💵 300k+", "❓ Consultation"], ["❌ Cancel Order"]]
    await update.message.reply_text("💰 သင့် Budget Range ကို ရွေးချယ်ပါ", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return BUDGET

async def set_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["budget"] = update.message.text
    od = context.user_data["order"]
    
    summary = (
        "⚠️ **အော်ဒါ အတည်ပြုရန် စစ်ဆေးပါ**\n\n"
        f"📦 Package: {od['package']}\n"
        f"🤖 Bot Type: {od['bot_type']}\n"
        f"📝 Idea: {od['description']}\n"
        f"⚙️ Features: {od['features']}\n"
        f"👤 Info: {od['customer_info']}\n"
        f"💰 Budget: {od['budget']}\n\n"
        "အချက်အလက်များ မှန်ကန်ပါက '✅ အော်ဒါ Confirm လုပ်မည်' ကိုနှိပ်ပါ။"
    )
    keyboard = [["✅ အော်ဒါ Confirm လုပ်မည်", "✏️ အစမှ ပြန်ပြင်မည်"], ["❌ Cancel Order"]]
    await update.message.reply_text(summary, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
    return CONFIRMATION

async def order_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "✏️ အစမှ ပြန်ပြင်မည်":
        context.user_data["order"] = {}
        keyboard = [["🤖 Starter", "🤖 Standard"], ["🤖 Premium (Custom)"], ["❌ Cancel Order"]]
        await update.message.reply_text("🔄 အော်ဒါ အသစ်ပြန်တင်ရန် Package ရွေးချယ်ပါ။", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return PACKAGE_TYPE
        
    if text == "✅ အော်ဒါ Confirm လုပ်မည်":
        user = update.message.from_user
        od = context.user_data["order"]
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                """INSERT INTO orders (user_id, name, username, customer_info, bot_type, description, features, budget, status, created_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user.id, user.first_name, f"@{user.username}", od["customer_info"], od["bot_type"], od["description"], od["features"], od["budget"], "Pending 🟡", current_date, current_date)
            )
            order_number = cursor.lastrowid
            order_id = f"MMB-{datetime.now().strftime('%Y%m%d')}-{order_number:04d}"
            await db.execute("UPDATE orders SET order_id = ? WHERE id = ?", (order_id, order_number))
            await db.commit()

        await update.message.reply_text(f"✅ **Order တင်ခြင်း အောင်မြင်ပါပြီ**\n\n📌 Order ID: `{order_id}`\n\nDeveloper မှ မကြာမီ ဆက်သွယ်ပေးပါမည်။", reply_markup=get_main_menu(), parse_mode="Markdown")
        
        # Notify Admin
        admin_text = f"📩 **NEW ORDER**\n\n📌 ID: `{order_id}`\n👤 Name: {user.first_name}\n📦 Package: {od['package']}\n💰 Budget: {od['budget']}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="Markdown")
        
        return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ လုပ်ဆောင်ချက် ပယ်ဖျက်လိုက်ပါပြီ။", reply_markup=get_main_menu())
    return ConversationHandler.END

# ==========================================================
# RICH MEDIA BROADCAST SYSTEM
# ==========================================================
BROADCAST_RECEIVE = 20

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID: return
    keyboard = [["❌ Cancel Broadcast"]]
    await update.message.reply_text("📢 Broadcast ပို့ရန် စာသား၊ ပုံ (သို့) Video ကို ယခု ပေးပို့ပါ။", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return BROADCAST_RECEIVE

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Cancel Broadcast":
        await update.message.reply_text("❌ Broadcast ပယ်ဖျက်လိုက်ပါပြီ။", reply_markup=get_main_menu())
        return ConversationHandler.END

    msg_id = update.message.message_id
    admin_id = update.message.chat_id
    
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE is_banned = 0") as cursor:
            users = await cursor.fetchall()

    await update.message.reply_text(f"📢 Broadcast စတင်ပို့ဆောင်နေပါပြီ... (Users: {len(users)})", reply_markup=get_main_menu())
    
    success = 0
    for row in users:
        try:
            await context.bot.copy_message(chat_id=row[0], from_chat_id=admin_id, message_id=msg_id)
            success += 1
            await asyncio.sleep(0.05) # Prevent Telegram Flood Limits
        except: pass
        
    await update.message.reply_text(f"✅ Broadcast ပြီးစီးပါပြီ။ အောင်မြင်စွာပို့နိုင်သူ: {success} ဦး")
    return ConversationHandler.END

# ==========================================================
# ADVANCED ADMIN DASHBOARD
# ==========================================================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID: return
    
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c: users_count = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM orders") as c: orders_count = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_banned=1") as c: banned_count = (await c.fetchone())[0]

    text = f"💻 **Admin Dashboard**\n\n👥 Users: {users_count}\n📦 Orders: {orders_count}\n🚫 Banned: {banned_count}"
    keyboard = [
        [InlineKeyboardButton("📊 Database Export", callback_data="admin_export")],
        [InlineKeyboardButton("📢 Broadcast (Command သုံးရန်)", callback_data="admin_noop")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_export":
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT * FROM orders") as cursor:
                rows = await cursor.fetchall()
        
        filename = "orders_db.csv"
        with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerows(rows)
            
        with open(filename, "rb") as doc:
            await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=doc, filename=filename)
        os.remove(filename)

# ==========================================================
# MAIN DISPATCHER
# ==========================================================
def main():
    app = Application.builder().token(BOT_TOKEN).post_init(init_db).build()

    # 1. Security Middleware (Group -1 runs before anything else)
    app.add_handler(TypeHandler(Update, security_middleware), group=-1)

    # 2. Order Conversation
    order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🛒 Bot မှာယူရန်$"), start_order)],
        states={
            PACKAGE_TYPE: [MessageHandler(filters.TEXT & ~filters.Regex("^❌"), set_package_type)],
            BOT_TYPE: [MessageHandler(filters.TEXT & ~filters.Regex("^❌"), set_bot_type)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.Regex("^❌"), set_description)],
            FEATURES: [MessageHandler(filters.TEXT & ~filters.Regex("^❌"), set_features)],
            CUSTOMER_INFO: [MessageHandler(filters.TEXT & ~filters.Regex("^❌"), set_customer_info)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.Regex("^❌"), set_budget)],
            CONFIRMATION: [MessageHandler(filters.Regex("^(✅ အော်ဒါ Confirm လုပ်မည်|✏️ အစမှ ပြန်ပြင်မည်)$"), order_confirmation)]
        },
        fallbacks=[MessageHandler(filters.Regex("^❌"), cancel_order)]
    )
    app.add_handler(order_handler)

    # 3. Profile Conversation
    prof_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_profile_start, pattern="^edit_profile$")],
        states={
            PROF_PHONE: [MessageHandler(filters.TEXT, save_prof_phone)],
            PROF_BIZ: [MessageHandler(filters.TEXT, save_prof_biz)]
        },
        fallbacks=[]
    )
    app.add_handler(prof_handler)

    # 4. Broadcast Conversation
    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_start)],
        states={BROADCAST_RECEIVE: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_send)]},
        fallbacks=[MessageHandler(filters.Regex("^❌"), cancel_order)]
    )
    app.add_handler(broadcast_conv)

    # Basic Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    
    # Review Handlers
    app.add_handler(MessageHandler(filters.Regex("^⭐ Customer Review$"), show_reviews))
    app.add_handler(MessageHandler(filters.Regex("^⭐⭐⭐.*"), save_review))

    # Menu Triggers
    app.add_handler(MessageHandler(filters.Regex("^⚙️ My Profile$"), my_profile))
    app.add_handler(MessageHandler(filters.Regex("^(🏠 ပင်မမီနူးသို့ ပြန်ရန်|🔙 နောက်ပြန်ဆုပ်ရန်)$"), lambda u, c: u.message.reply_text("ပင်မမီနူး-", reply_markup=get_main_menu())))

    # Admin Callback
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))

    print("🚀 MM Bot Market Security Engine Active...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
