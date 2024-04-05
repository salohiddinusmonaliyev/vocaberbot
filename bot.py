import logging
import random

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler

import requests

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

START = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            KeyboardButton("💪 Yodlash"),
            KeyboardButton("📝 Topshirish"),
        ],
        [KeyboardButton("➕ So'z qo'shish")],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Quyidagilarni birini tanlang.", reply_markup=reply_markup)
    return START

async def memorize(update: Update, context):
    words = (requests.get("http://127.0.0.1:8000/words/").json())
    selected_word = random.choice(words)
    await update.message.reply_html(text=f"{selected_word["word"]}\n{selected_word["definition"]}")

async def test(update: Update, context):
    words = (requests.get("http://127.0.0.1:8000/words/").json())
    print(words)
    selected_word = random.choice(words)
    print(selected_word["word"])
    await update.message.reply_html(text=f"{selected_word["word"]}\nBu so'zni bilasizmi?")
    await update.message.reply_html(text="Topshirish")

async def add(update: Update, context):
    query = update.callback_query
    await update.message.reply_html(text="So'z qo'shish")

async def organizer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "💪 Yodlash":
        return await memorize(update, context)
    elif text == "📝 Topshirish":
        return await test(update, context)
    elif text == "➕ So'z qo'shish":
        return await add(update, context)


def main() -> None:
    application = Application.builder().token("6756942822:AAF2rdWfH-9qrqQHsFb4fkQuD66RTsjSwd8").build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            START: [MessageHandler(filters.TEXT, organizer)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()