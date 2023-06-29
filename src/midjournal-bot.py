"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import time
import imageHandler
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}, send a picture to see what you will get!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("This bot is part of an experimental research. Authors: Bruno Sabino e Kizzy Terra")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)
    # ai_img_path = "img/ai_img.png"
    # await update.message.reply_photo(photo=open(ai_img_path, "rb"))

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    img_file = await update.message.photo[-1].get_file()
    img_name = f'{user.first_name.lower()}_{time.time()}.jpg'
    img_path = "img/users/" + img_name

    await img_file.download_to_drive(img_path)
    logger.info("Photo of %s: %s", user.first_name, img_name)
    await update.message.reply_text(f"Gerando imagem...")
    ai_img_path, prompt = handle_image(img_name)
    if ai_img_path == '':
        await update.message.reply_text(f"Tempo excedido! Tente novamente com outra imagem.")
    else: 
        await update.message.reply_photo(photo=open(ai_img_path, "rb"))
        await update.message.reply_text(f"Descrição: {prompt}")
         


def handle_image(img_name):
        
        # img_sender = sender.Sender()
        # prompt = img_sender.describe_static()
        # prompt = sender.describe(img_path)
        # img_sender.imagine(prompt)
        handler = imageHandler.ImageHandler(img_name)
        return handler.get_ai_img()


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    arquivo = open("secure-files/token.txt")
    token = arquivo.read()
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.PHOTO, photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    main()
