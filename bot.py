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

START, MEMORIZE = range(2)

words = (requests.get("http://127.0.0.1:8000/word/").json())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            KeyboardButton("💪 Yodlash"),
            KeyboardButton("📝 Topshirish"),
        ],
        [KeyboardButton("➕ So'z qo'shish")],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    if update.message:
        await update.message.reply_text("Quyidagilarni birini tanlang.", reply_markup=reply_markup)
    elif update.callback_query and update.callback_query.message:
        await context.bot.deleteMessage(chat_id=update.callback_query.from_user.id, message_id=next_word_message.id)
        await update.callback_query.message.reply_text("Quyidagilarni birini tanlang.", reply_markup=reply_markup)
    else:
        logger.error("Cannot send message: Both update.message and update.callback_query.message are None.")

    return START

async def memorize(update: Update, context):
    global words
    if not words:
        words = (requests.get("http://127.0.0.1:8000/word/").json())
    words1 = []
    users = requests.get("http://127.0.0.1:8000/telegram-users/").json()
    for user in users:
        if user["telegram_id"]==str(update.effective_user.id):
            user_id = user["id"]
    for i in words:
        if i["user"] == user_id:
            words1.append(i)
    selected_word = random.choice(words1)
    keyboard = [
        [InlineKeyboardButton("➡️ Keyingi so'z", callback_data="next_word")],
        [InlineKeyboardButton("🛑 Tugatish", callback_data="stop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    global next_word_message
    word = selected_word['word']
    definition = selected_word['definition']
    words.remove(selected_word)
    next_word_message = await context.bot.send_message(chat_id=update.effective_user.id, text=f"{word.title()}\n👉 {definition}", reply_markup=reply_markup)

    return MEMORIZE
    
async def next_word(update: Update, context):
    query = update.callback_query
    global next_word_message
    await context.bot.deleteMessage(chat_id=query.from_user.id, message_id=next_word_message.id)
    await query.answer()
    
    await memorize(update, context)

async def test(update: Update, context):
    words = (requests.get("http://127.0.0.1:8000/word/").json())
    selected_word = random.choice(words)
    await update.message.reply_html(text=f"{selected_word["word"]}\nBu so'zni bilasizmi?")
    return START

async def add(update: Update, context):
    query = update.callback_query
    await update.message.reply_html(text="So'z qo'shish")
    return START

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
            CommandHandler("again", memorize),
            
        ],
        states={
            START: [MessageHandler(filters.TEXT, organizer)],
            MEMORIZE: [
                MessageHandler(filters.TEXT, organizer),
                CallbackQueryHandler(next_word, pattern='^next_word$'),
                CallbackQueryHandler(start, pattern="^stop$")
            ],

        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()