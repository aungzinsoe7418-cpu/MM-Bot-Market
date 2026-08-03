
import os
import logging
import sqlite3
import threading

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
    filters
)


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================================================
# KEEP ALIVE SERVER
# ==========================================================

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.end_headers()

        self.wfile.write(
            b"MM Bot Market is Active!"
        )


def run_server():

    port = int(
        os.environ.get(
            "PORT",
            8080
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        SimpleHTTPRequestHandler
    )

    logging.info(
        f"Keep Alive Server Running : {port}"
    )

    server.serve_forever()



threading.Thread(
    target=run_server,
    daemon=True
).start()



# ==========================================================
# CONFIGURATION
# ==========================================================


# Admin Telegram ID
ADMIN_CHAT_ID = 8582190375


# Developer Username
DEVELOPER_USERNAME = "superraizo7"



# IMPORTANT
# Put your NEW BotFather Token here

BOT_TOKEN = os.environ.get(
    "BOT_TOKEN",
    "8912157146:AAEjdIl3Dy36mey4GJenjrCypNOq9TLSK4o "
)



# ==========================================================
# CONVERSATION STATES
# ==========================================================

BOT_TYPE, DESCRIPTION, FEATURES, CUSTOMER_INFO, BUDGET = range(5)

ORDER_SEARCH = 5



# ==========================================================
# DATABASE
# ==========================================================

DB_NAME = "mm_bot_market.db"



def get_db():

    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )



def init_db():

    conn = get_db()

    cursor = conn.cursor()


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


    conn.commit()

    conn.close()



init_db()



# ==========================================================
# MAIN MENU
# ==========================================================


def get_main_menu():

    keyboard = [

        [
            "🤖 ဝန်ဆောင်မှုများ",
            "💰 စျေးနှုန်းများ"
        ],

        [
            "🎬 Demo / Portfolio",
            "🛒 Bot မှာယူရန်"
        ],

        [
            "⭐ Customer Review",
            "❓ FAQ"
        ],

        [
            "📦 My Order Status",
            "👨‍💻 Developer နှင့် ဆွေးနွေးရန်"
        ]

    ]


    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )



# ==========================================================
# START
# ==========================================================


async def start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    text = (

        "🤖 **MM Bot Market မှ ကြိုဆိုပါတယ်**\n\n"

        "သင့် Business အတွက် Professional "
        "Telegram Bot များကို စိတ်ကြိုက် "
        "ဖန်တီးပေးပါတယ်။\n\n"

        "ကျွန်ုပ်တို့ ဖန်တီးပေးနိုင်သော Bot များ👇\n\n"

        "🛒 Online Shop Bot\n"
        "🎮 Game Top-up Bot\n"
        "📢 Telegram Channel Bot\n"
        "🤖 AI Chat Bot\n"
        "🏢 Business Automation Bot\n"
        "✍️ Custom Bot\n\n"

        "သင့်လုပ်ငန်းအတွက် သင့်တော်သော "
        "Bot Solution ကို ရွေးချယ်ပါ 👇"

    )


    await update.message.reply_text(

        text,

        reply_markup=get_main_menu(),

        parse_mode="Markdown"

    )



# ==========================================================
# SERVICES
# ==========================================================


async def show_services(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    text = (

        "🛒 **Telegram Shop Bot**\n"
        "Features: Product Catalog, Order System, Customer Database, Auto Reply\n\n"


        "🎮 **Game Top-up Bot**\n"
        "Features: Order Form, Payment System, Admin Control\n\n"


        "📢 **Channel Management Bot**\n"
        "Features: Auto Post, Auto Reply, Member System\n\n"


        "🤖 **AI Chat Bot**\n"
        "Features: AI Assistant, Customer Support, FAQ System\n\n"


        "🏢 **Business Automation Bot**\n"
        "Features: Booking, Database, Workflow Automation\n\n"


        "✍️ **Custom Bot**\n"
        "Features: Fully Customized Solution\n\n"


        "-----------------------------\n"

        "🛒 Bot မှာယူရန် Button ကို နှိပ်ပြီး "
        "Order တင်နိုင်ပါတယ်။"

    )


    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )



# ==========================================================
# PRICING
# ==========================================================


async def show_pricing(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    text = (

        "💰 **Bot Development Price**\n\n"

        "🥉 Basic Bot\n"
        "50,000 MMK - 100,000 MMK\n\n"

        "🥈 Medium Bot\n"
        "100,000 MMK - 300,000 MMK\n\n"

        "🥇 Advanced Bot\n"
        "300,000 MMK +\n\n"

        "💡 Final price depends on Features, "
        "Database and Complexity."

    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )



# ==========================================================
# PORTFOLIO
# ==========================================================


async def show_portfolio(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    text = (

        "🎬 **Demo / Portfolio**\n\n"

        "🤖 Shop Bot Demo\n"
        "🎮 Game Top-up Bot Demo\n"
        "📢 Channel Management Bot Demo\n"
        "🧠 AI Assistant Bot Demo\n"
        "🏢 Business Automation Demo\n\n"

        "Demo များနှင့် အသေးစိတ်အချက်အလက်များကို "
        "Developer ထံ ဆက်သွယ်မေးမြန်းနိုင်ပါတယ်။"

    )


    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )



# ==========================================================
# CUSTOMER REVIEWS
# ==========================================================


async def show_reviews(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    text = (

        "⭐ **Customer Reviews**\n\n"

        "⭐⭐⭐⭐⭐\n"
        "\"Professional Bot Service\"\n\n"

        "⭐⭐⭐⭐⭐\n"
        "\"Fast Delivery & Good Support\"\n\n"

        "⭐⭐⭐⭐⭐\n"
        "\"စိတ်တိုင်းကျ Design နှင့် Function များရရှိပါတယ်\""

    )


    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )



# ==========================================================
# FAQ
# ==========================================================


async def show_faq(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    text = (

        "❓ **Frequently Asked Questions**\n\n"


        "Q: Bot ဖန်တီးဖို့ ဘယ်လောက်ကြာပါသလဲ?\n"

        "A: Bot Complexity ပေါ်မူတည်ပြီး "
        "၃ ရက်မှ ၁၄ ရက်အထိ ကြာနိုင်ပါတယ်။\n\n"



        "Q: ရှိပြီးသား Bot ကို ပြင်ဆင်နိုင်ပါသလား?\n"

        "A: ရပါတယ်။ Update နှင့် Modify "
        "ပြုလုပ်ပေးနိုင်ပါတယ်။\n\n"



        "Q: Delivery ပြီးရင် Support ရပါသလား?\n"

        "A: ရပါတယ်။ Basic Support ပေးပါမည်။"

    )


    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )



# ==========================================================
# DEVELOPER CONTACT
# ==========================================================


async def developer_contact(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    keyboard = [

        [

            InlineKeyboardButton(
                "👨‍💻 Developer ထံ ဆက်သွယ်ရန်",
                url=f"https://t.me/{DEVELOPER_USERNAME}"
            )

        ]

    ]


    await update.message.reply_text(

        "Developer နှင့် တိုက်ရိုက် "
        "ဆွေးနွေးလိုပါက Button ကို နှိပ်ပါ 👇",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )



# ==========================================================
# ORDER START
# ==========================================================


async def start_order(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    context.user_data["order"] = {}



    keyboard = [

        [
            "🛒 Shop Bot",
            "🎮 Game Top-up Bot"
        ],

        [
            "🤖 AI Chat Bot",
            "📢 Channel Bot"
        ],

        [
            "🏢 Business Bot",
            "✍️ Custom Bot"
        ]

    ]



    await update.message.reply_text(

        "🤖 သင်ဖန်တီးလိုသော Bot အမျိုးအစားကို ရွေးချယ်ပါ",

        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

    )


    return BOT_TYPE



# ==========================================================
# BOT TYPE
# ==========================================================


async def set_bot_type(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    context.user_data["order"]["bot_type"] = (
        update.message.text
    )


    await update.message.reply_text(

        "📝 သင်လိုချင်သော Bot Idea နှင့် "
        "လိုအပ်သော Function များကို ရေးပေးပါ။"

    )


    return DESCRIPTION



# ==========================================================
# DESCRIPTION
# ==========================================================


async def set_description(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    context.user_data["order"]["description"] = (
        update.message.text
    )


    keyboard = [

        [
            "✅ Auto Reply",
            "✅ Payment System"
        ],

        [
            "✅ Database",
            "✅ Admin Panel"
        ],

        [
            "✅ User Management",
            "✅ AI Function"
        ]

    ]


    await update.message.reply_text(

        "⚙️ လိုအပ်သော Function ကိုရွေးပါ "
        "သို့မဟုတ် စာဖြင့်ရေးပို့ပါ",

        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

    )


    return FEATURES



# ==========================================================
# FEATURES
# ==========================================================


async def set_features(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    context.user_data["order"]["features"] = (
        update.message.text
    )



    await update.message.reply_text(

        "👤 သင့်အမည်၊ Phone Number နှင့် "
        "Business Type ကို ရေးပေးပါ။\n\n"

        "ဥပမာ - Aung, 09123456789, Online Shop"

    )


    return CUSTOMER_INFO



# ==========================================================
# CUSTOMER INFO
# ==========================================================


async def set_customer_info(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    context.user_data["order"]["customer_info"] = (
        update.message.text
    )


    keyboard = [

        [
            "💵 50,000 MMK အောက်",
            "💵 50,000 - 200,000 MMK"
        ],

        [
            "💵 200,000 MMK အထက်",
            "❓ Consultation လိုအပ်ပါတယ်"
        ]

    ]



    await update.message.reply_text(

        "💰 သင့် Budget Range ကို ရွေးချယ်ပါ",

        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

    )


    return BUDGET



# ==========================================================
# SET BUDGET & SAVE ORDER
# ==========================================================


async def set_budget(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    order_data = context.user_data["order"]

    order_data["budget"] = update.message.text


    user = update.message.from_user


    username = (
        f"@{user.username}"
        if user.username
        else "No Username"
    )


    current_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    conn = get_db()

    cursor = conn.cursor()



    cursor.execute(
        """
        INSERT INTO orders
        (
            user_id,
            name,
            username,
            customer_info,
            bot_type,
            description,
            features,
            budget,
            status,
            created_date,
            updated_date
        )

        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,

        (

            user.id,

            user.first_name,

            username,

            order_data["customer_info"],

            order_data["bot_type"],

            order_data["description"],

            order_data["features"],

            order_data["budget"],

            "Pending 🟡",

            current_date,

            current_date

        )

    )


    order_number = cursor.lastrowid


    order_id = (
        f"MMB-{datetime.now().strftime('%Y%m%d')}-"
        f"{order_number:04d}"
    )


    cursor.execute(
        """
        UPDATE orders

        SET order_id = ?

        WHERE id = ?

        """,

        (
            order_id,
            order_number
        )

    )


    conn.commit()

    conn.close()



    # CUSTOMER MESSAGE

    summary = (

        "✅ **Order တင်ခြင်း အောင်မြင်ပါပြီ**\n\n"

        f"📌 Order ID: `{order_id}`\n\n"

        f"🤖 Bot Type: {order_data['bot_type']}\n"

        f"📝 Description: {order_data['description']}\n"

        f"⚙️ Features: {order_data['features']}\n"

        f"💰 Budget: {order_data['budget']}\n\n"

        "Developer မှ စစ်ဆေးပြီး "
        "မကြာမီ ဆက်သွယ်ပေးပါမည်။"

    )


    await update.message.reply_text(

        summary,

        reply_markup=get_main_menu(),

        parse_mode="Markdown"

    )



    # ADMIN ALERT


    admin_text = (

        "📩 **NEW BOT ORDER**\n\n"

        f"📌 Order ID: `{order_id}`\n"

        f"👤 Customer: {user.first_name}\n"

        f"📱 Username: {username}\n\n"

        f"🤖 Bot: {order_data['bot_type']}\n"

        f"📝 Idea: {order_data['description']}\n"

        f"⚙️ Feature: {order_data['features']}\n"

        f"💰 Budget: {order_data['budget']}\n\n"

        f"📅 Date: {current_date}"

    )


    try:

        await context.bot.send_message(

            chat_id=ADMIN_CHAT_ID,

            text=admin_text,

            parse_mode="Markdown"

        )


    except Exception as error:

        logging.error(error)



    return ConversationHandler.END




# ==========================================================
# ORDER STATUS
# ==========================================================


async def request_order_id(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    await update.message.reply_text(

        "🔍 Order ID ရိုက်ထည့်ပါ\n\n"
        "ဥပမာ - MMB-20260803-0001"

    )


    return ORDER_SEARCH




async def check_order_status(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    order_id = (
        update.message.text
        .strip()
        .upper()
    )


    conn = get_db()

    cursor = conn.cursor()



    cursor.execute(

        """
        SELECT
        order_id,
        status,
        updated_date

        FROM orders

        WHERE order_id = ?

        """,

        (
            order_id,
        )

    )


    result = cursor.fetchone()


    conn.close()



    if result:


        message = (

            "📦 **Order Status**\n\n"

            f"📌 ID: `{result[0]}`\n"

            f"📊 Status: {result[1]}\n"

            f"🕒 Update: {result[2]}"

        )


    else:


        message = (

            "❌ Order ID မတွေ့ပါ။\n"

            "Order ID ကို ပြန်စစ်ပေးပါ။"

        )



    await update.message.reply_text(

        message,

        reply_markup=get_main_menu(),

        parse_mode="Markdown"

    )


    return ConversationHandler.END




# ==========================================================
# MAIN DISPATCHER
# ==========================================================


def main():


    app = Application.builder().token(
        BOT_TOKEN
    ).build()



    order_handler = ConversationHandler(

        entry_points=[

            MessageHandler(
                filters.Regex(
                    "^🛒 Bot မှာယူရန်$"
                ),

                start_order
            )

        ],


        states={


            BOT_TYPE:[

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    set_bot_type
                )

            ],


            DESCRIPTION:[

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    set_description
                )

            ],


            FEATURES:[

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    set_features
                )

            ],


            CUSTOMER_INFO:[

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    set_customer_info
                )

            ],


            BUDGET:[

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    set_budget
                )

            ]

        },


        fallbacks=[]

    )




    status_handler = ConversationHandler(

        entry_points=[

            MessageHandler(
                filters.Regex(
                    "^📦 My Order Status$"
                ),

                request_order_id
            )

        ],


        states={

            ORDER_SEARCH:[

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    check_order_status
                )

            ]

        },


        fallbacks=[]

    )



    # COMMAND

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )



    # BUTTONS


    app.add_handler(
        MessageHandler(
            filters.Regex("^🤖 ဝန်ဆောင်မှုများ$"),
            show_services
        )
    )


    app.add_handler(
        MessageHandler(
            filters.Regex("^💰 စျေးနှုန်းများ$"),
            show_pricing
        )
    )


    app.add_handler(
        MessageHandler(
            filters.Regex("^🎬 Demo / Portfolio$"),
            show_portfolio
        )
    )


    app.add_handler(
        MessageHandler(
            filters.Regex("^⭐ Customer Review$"),
            show_reviews
        )
    )


    app.add_handler(
        MessageHandler(
            filters.Regex("^❓ FAQ$"),
            show_faq
        )
    )


    app.add_handler(
        MessageHandler(
            filters.Regex("^👨‍💻 Developer နှင့် ဆွေးနွေးရန်$"),
            developer_contact
        )
    )



    app.add_handler(order_handler)

    app.add_handler(status_handler)



    print(
        "MM Bot Market Professional Version Started..."
    )


    app.run_polling()



# ==========================================================
# RUN
# ==========================================================


if __name__ == "__main__":

    main()
