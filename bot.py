import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

BOT_TOKEN = os.getenv("8773987826:AAFvEkqsk9FnfFSqq_ZVoCTLuKP93erQWSc")
ADMIN_USERNAME = "arjunbhumihar143"
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")  # Optional: your numeric Telegram chat ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Contact Admin", callback_data="contact")],
        [InlineKeyboardButton("💬 Chat with Admin", callback_data="chat")],
        [InlineKeyboardButton("📞 Call Admin", callback_data="call")],
        [InlineKeyboardButton("ℹ️ About Admin", callback_data="about")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Please choose an option below:",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "contact":
        await query.message.reply_text(
            f"Contact the owner here: @{ADMIN_USERNAME}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "Open Owner Profile",
                    url=f"https://t.me/{ADMIN_USERNAME}"
                )],
                [InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ])
        )

    elif query.data == "chat":
        context.user_data["waiting_for_message"] = True
        await query.message.reply_text(
            "The owner is currently having a meal. "
            "Please leave your message and wait for a reply.\n\n"
            "Send your message now:"
        )

    elif query.data == "call":
        await query.message.reply_text(
            "The owner is currently sleeping. Please try again later.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ])
        )

    elif query.data == "about":
        await query.message.reply_text(
            f"👤 Owner: @{ADMIN_USERNAME}\n"
            "📌 Status: Temporarily unavailable\n"
            "💬 You can leave a message through the Chat option.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ])
        )

    elif query.data == "back":
        await query.message.edit_text(
            "Welcome! Please choose an option below:",
            reply_markup=main_menu()
        )

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_message"):
        return

    text = update.message.text
    user = update.effective_user
    user_label = f"@{user.username}" if user.username else user.full_name

    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    "🔔 New Admin Request\n\n"
                    f"From: {user_label}\n"
                    f"User ID: {user.id}\n"
                    f"Message: {text}"
                )
            )
        except Exception:
            logger.exception("Could not notify admin.")

    await update.message.reply_text(
        "Your message has been received. "
        f"The owner (@{ADMIN_USERNAME}) will review it when available.",
        reply_markup=main_menu()
    )
    context.user_data["waiting_for_message"] = False

def run():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise SystemExit(
            "Set BOT_TOKEN in your environment before running the bot."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    app.run_polling()

if __name__ == "__main__":
    run()
