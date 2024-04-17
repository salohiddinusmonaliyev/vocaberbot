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

START, MEMORIZE, TEST, ADD_WORD, ADD_DEFINITION = range(4)

words = (requests.get("http://127.0.0.1:8000/word/").json())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            KeyboardButton("💪 Yodlash"),
            KeyboardButton("📝 Topshirish"),
        ],
        [
            KeyboardButton("➕ So'z qo'shish"),
            KeyboardButton("📃 So'zlar ro'yhati"),
         ],
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
    next_word_message = await context.bot.send_message(chat_id=update.effective_user.id, text=f"<b>{word.title()}</b>\n👉 {definition}", reply_markup=reply_markup, parse_mode='HTML')

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
    keyboard = [
        [InlineKeyboardButton("Ha", callback_data="next_word_test"),
         InlineKeyboardButton("Yo'q", callback_data="next_word_test")],
        [InlineKeyboardButton("🛑 Tugatish", callback_data="stop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    global next_word_message_test
    next_word_message_test = await update.message.reply_html(text=f"{selected_word["word"]}\nBu so'zni bilasizmi?", reply_markup=reply_markup)
    return TEST

async def next_word_test(update: Update, context):
    query = update.callback_query
    global next_word_message_test
    await context.bot.deleteMessage(chat_id=query.from_user.id, message_id=next_word_message_test.id)
    await query.answer()

    await test(update, context)

async def add_word(update: Update, context):
    added_word = update.message.text
    context.chat_data['added_word'] = added_word

    cancel_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Bekor qilish", callback_data="cancel")],
    ])
    await update.message.reply_html(text="So'z uchun <b>definition</b> yuboring.", reply_markup=cancel_btn)
    return ADD_DEFINITION

async def add_definition(update: Update, context):
    definition = update.message.text
    added_word = context.chat_data.get('added_word')
    users = requests.get("http://127.0.0.1:8000/telegram-users/").json()
    for user in users:
        if user["telegram_id"]==str(update.effective_user.id):
            user_id = user["id"]
    json_data = {
        "word": added_word,
        "definition": definition,
        "user": user_id,
    }
    order_response = requests.post(url="http://127.0.0.1:8000/word/", json=json_data)
    await update.message.reply_html("🎉 So'z qo'shildi")
    return ConversationHandler.END

async def organizer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "💪 Yodlash":
        await context.bot.send_message(chat_id=update.effective_user.id, text="Boshqa so'zga o'tish uchun <b>\"➡️ Keyingi so'z\"</b> tugmasini bosing.", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')

        return await memorize(update, context)
    elif text == "📝 Topshirish":
        return await test(update, context)
    elif text == "➕ So'z qo'shish":
        cancel_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Bekor qilish", callback_data="cancel")],
    ])
        await update.message.reply_html("So'zni yuboring", reply_markup=cancel_btn)
        return ADD_WORD
    elif text =="📃 So'zlar ro'yhati":
        words = (requests.get("http://127.0.0.1:8000/word/").json())
        words1 = []
        users = requests.get("http://127.0.0.1:8000/telegram-users/").json()
        for user in users:
            if user["telegram_id"]==str(update.effective_user.id):
                user_id = user["id"]
        for i in words:
            if i["user"] == user_id:
                words1.append(i)
        formatted_text = "\n\n".join([f"<b>{item['word'].capitalize()}</b>\n👉 {item['definition']}" for item in words1])
        await update.message.reply_html(formatted_text)

async def cancel(update, context):
    await update.callback_query.message.reply_text("Bekor qilindi")
    return START

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
            TEST: [
                MessageHandler(filters.TEXT, organizer),
                CallbackQueryHandler(next_word_test, pattern='^next_word_test$'),
                CallbackQueryHandler(start, pattern="^stop$")
            ]
            ADD_WORD: [MessageHandler(filters.TEXT, add_word),
                       CallbackQueryHandler(cancel, pattern='^cancel$'),],
            ADD_DEFINITION: [MessageHandler(filters.TEXT, add_definition),
                             CallbackQueryHandler(cancel, pattern='^cancel$'),],


        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()