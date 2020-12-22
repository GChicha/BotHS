import glob
import logging
import os

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Updater,
)
from telegram.files.location import Location
from telegram.files.venue import Venue
from telegram.parsemode import ParseMode

logger = logging.getLogger()

TOKEN = os.environ["TOKEN"]


# COMANDOS ESTATICOS:
def localizacao(update: Update, context: CallbackContext):
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_venue(
            reply_to_message_id=update.effective_message.message_id,
            venue=Venue(
                title="Hackerspace Maringá",
                address="R. Vitória, 943 - Vila Esperanca, Maringá - PR",
                google_place_id="ChIJr9L4qzLR7JQRWi8Anh8JyCI",
                google_place_type="zoo",
                location=Location(latitude=-23.402309060129333,
                                  longitude=-51.93850697016083)))


def regras(update: Update, context: CallbackContext):
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_message(
            reply_to_message_id=update.effective_message.message_id,
            text=open("static_messages/rules.md").read(),
            parse_mode=ParseMode.MARKDOWN_V2)


def help(update: Update, context: CallbackContext):
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_message(
            reply_to_message_id=update.effective_message.message_id,
            text=open("static_messages/rules.md").read(),
            parse_mode=ParseMode.MARKDOWN_V2)


#COMANDOS DINAMICOS:
def newsletter(update: Update, context: CallbackContext):
    newest_file = max(glob.iglob('./news/*.pdf'), key=os.path.getctime)
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_document(
            open(newest_file, "rb"),
            reply_to_message_id=update.effective_message.message_id,
            filename="newsletter_hs_maringa.pdf",
            caption="Newsletter Hackerspace Maringá")


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    #COMANDOS ESTATICOS
    dispatcher.add_handler(CommandHandler('address', localizacao))
    dispatcher.add_handler(CommandHandler('rules', regras))
    dispatcher.add_handler(CommandHandler('help', help))

    #COMANDOS DINAMICOS
    dispatcher.add_handler(CommandHandler('news', newsletter))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
