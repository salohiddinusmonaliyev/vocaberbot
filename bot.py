import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("💪 Yodlash", callback_data="memorize"),
            InlineKeyboardButton("📝 Topshirish", callback_data="test"),
        ],
        [InlineKeyboardButton("➕ So'z qo'shish", callback_data="add")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Quyidagilarni birini tanlang.", reply_markup=reply_markup)

async def memorize(update: Update, context):
    query = update.callback_query
    await query.edit_message_text(text="Yodlash", reply_markup=back_key)

async def test(update: Update, context):
    query = update.callback_query
    await query.edit_message_text(text="Topshirish", reply_markup=back_key)

async def add(update: Update, context):
    query = update.callback_query
    await query.edit_message_text(text="So'z qo'shish", reply_markup=back_key)

async def organizer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data == "memorize":
        return await memorize(update, context)
    elif query.data == "test":
        return await test(update, context)
    elif query.data == "add":
        return await add(update, context)


def main() -> None:
    application = Application.builder().token("6756942822:AAF2rdWfH-9qrqQHsFb4fkQuD66RTsjSwd8").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(organizer))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()