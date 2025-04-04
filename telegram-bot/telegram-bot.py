#!/usr/bin/env python

import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import google.generativeai as genai

with open("GOOGLEAPIKEY.txt","r") as g:
    GOOGLEAPIKEY = g.readline().strip()

with open("TELEGRAMAPIKEY.txt","r") as t:
    TELEGRAMAPIKEY = t.readline().strip()

genai.configure(api_key=GOOGLEAPIKEY)

model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    chat.send_message("You are the telegram chatbot of Athernos, an educational platform which adapts to each student's needs. You will chat with students and teachers, and answer their queries with respect to the outcome")
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}, I am the Telegram bot for Athenos, At your service!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I am the Telegram bot for Athenos, At your service!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    response = chat.send_message(update.message.text)
    await update.message.reply_text(response.text)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAMAPIKEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
