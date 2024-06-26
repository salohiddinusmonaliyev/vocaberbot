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

URL = "http://127.0.0.1:8000"
TOKEN = "6756942822:AAF2rdWfH-9qrqQHsFb4fkQuD66RTsjSwd8"

START, MEMORIZE, TEST, ADD_WORD, ADD_DEFINITION = range(5)

words = (requests.get(f"{URL}/word/").json())

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
        await update.callback_query.message.reply_text("Quyidagilarni birini tanlang.", reply_markup=reply_markup)
    else:
        logger.error("Cannot send message: Both update.message and update.callback_query.message are None.")

    return START

async def memorize(update: Update, context):
    global words
    if not words:
        words = (requests.get(f"{URL}/word/").json())
    words1 = []
    users = requests.get(f"{URL}/telegram-users/").json()
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
    word = selected_word['word']
    definition = selected_word['definition']
    words.remove(selected_word)
    next_word_message = await context.bot.send_message(chat_id=update.effective_user.id, text=f"<b>{word.title()}</b>\n👉 {definition}", reply_markup=reply_markup, parse_mode='HTML')
    context.user_data["next_word_message"] = next_word_message

    return MEMORIZE

async def next_word(update: Update, context):
    query = update.callback_query
    next_word_message = context.user_data.get("next_word_message")
    await context.bot.deleteMessage(chat_id=query.from_user.id, message_id=next_word_message.id)
    await query.answer()
    await memorize(update, context)

async def test(update: Update, context):
    words = (requests.get(f"{URL}/word/").json())
    keyboard = [
        [InlineKeyboardButton("🫣 Javobni ko'rsatish", callback_data="show_answer")],
        [InlineKeyboardButton("🛑 Tugatish", callback_data="stop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    global next_word_message
    selected_word = random.choice(words)
    context.user_data["selected_word"] = selected_word
    if update.message:
        next_word_message = await update.message.reply_html(text=f"<b>{selected_word["word"]}</b>", reply_markup=reply_markup)
    elif update.callback_query and update.callback_query.message:
        next_word_message = await update.callback_query.message.reply_html(text=f"<b>{selected_word["word"]}</b>", reply_markup=reply_markup)
    else:
        logger.error("Cannot send message: Both update.message and update.callback_query.message are None.")

    return TEST

async def show_answer(update: Update, context):
    query = update.callback_query
    selected_word = context.user_data.get('selected_word')
    button = [
        [InlineKeyboardButton("➡️ Keyingi so'z", callback_data="next_word")]
    ]
    await context.bot.edit_message_text(chat_id=query.from_user.id, message_id=next_word_message.id, text=f"<b>{selected_word['word']}</b>\n\n<i>👉 {selected_word['definition']}</i>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(button))

async def next_word_test(update: Update, context):
    query = update.callback_query
    global next_word_message
    await context.bot.deleteMessage(chat_id=query.from_user.id, message_id=next_word_message.id)
    await query.answer()
    await test(update, context)

async def stop(update: Update, context):
    query = update.callback_query
    global next_word_message
    await context.bot.deleteMessage(chat_id=query.from_user.id, message_id=next_word_message.id)
    await query.answer()
    return await start(update, context)

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
    users = requests.get(f"{URL}/telegram-users/").json()
    for user in users:
        if user["telegram_id"]==str(update.effective_user.id):
            user_id = user["id"]
    json_data = {
        "word": added_word,
        "definition": definition,
        "user": user_id,
    }
    order_response = requests.post(url=f"{URL}/word/", json=json_data)
    await update.message.reply_html("🎉 So'z qo'shildi")
    return ConversationHandler.END

async def delete(update: Update, context):
    await update.message.reply_html("So'zni o'chirish uchun so'z ID sini yuboring", reply_markup=ReplyKeyboardRemove())

async def organizer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "💪 Yodlash":
        await context.bot.send_message(chat_id=update.effective_user.id, text="Boshqa so'zga o'tish uchun <b>\"➡️ Keyingi so'z\"</b> tugmasini bosing.", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
        return await memorize(update, context)
    elif text == "📝 Topshirish":
        await context.bot.send_message(chat_id=update.effective_user.id, text="Javobni ko'rish va keyingi so'zga o'tish uchun <b>\"🫣 Javobni ko'rsatish\"</b> tugmasini bosing.", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
        return await test(update, context)
    elif text == "➕ So'z qo'shish":
        cancel_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Bekor qilish", callback_data="cancel")],
    ])
        await update.message.reply_html("So'zni yuboring", reply_markup=cancel_btn)
        return ADD_WORD
    elif text =="📃 So'zlar ro'yhati":
        words = (requests.get(f"{URL}/word/").json())
        words1 = []
        users = requests.get(f"{URL}/telegram-users/").json()
        for user in users:
            if user["telegram_id"]==str(update.effective_user.id):
                user_id = user["id"]
        for i in words:
            if i["user"] == user_id:
                words1.append(i)
        formatted_text = "\n\n".join([f"<b>{item['id']}. {item['word'].capitalize()}</b>\n👉 {item['definition']}" for item in words1])

        await update.message.reply_html(formatted_text, reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                    [
                        KeyboardButton(text="🗑 So'zni o'chirish")
                    ]
                ], resize_keyboard=True
        ))

    elif text == "🗑 So'zni o'chirish":
        return await delete(update, context)

async def cancel(update, context):
    await update.callback_query.message.reply_text("Bekor qilindi")
    return START

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            START: [MessageHandler(filters.TEXT, organizer)],
            MEMORIZE: [
                MessageHandler(filters.TEXT, organizer),
                CallbackQueryHandler(next_word, pattern='^next_word$'),
                CallbackQueryHandler(stop, pattern="^stop$")
            ],
            TEST: [
                MessageHandler(filters.TEXT, organizer),
                CallbackQueryHandler(show_answer, pattern='^show_answer$'),
                CallbackQueryHandler(next_word_test, pattern='^next_word$'),
                CallbackQueryHandler(stop, pattern="^stop$")
            ],

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