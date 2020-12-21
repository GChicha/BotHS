from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackContext
from telegram import Update, Bot

# COMANDOS ESTATICOS:
#Para primeiramente criar o comando, devemos definir uma função que
#ira compor o comando e retornar um texto

def localizacao(update: Update, context: CallbackContext):
    #Escrevemos o texto que o bot irá mandar
    resposta = "R. Vitória, 943 - Vila Esperanca, Maringá - PR"
    update.message.reply_text(resposta)

def regras(update: Update, context: CallbackContext):
    resposta = "Colocar texto aqui"
    update.message.reply_text(resposta)

def help(update: Update, context: CallbackContext):
    resposta = "Colocar texto aqui"
    update.message.reply_text(resposta)

def main():
    #Esse updater puxa nosso bot da API do telegram, esse token
    #é entregue quando criamos o bot.
    updater = Updater(token = '1461211618:AAFOImbh1IM0Yt9kzHbXLVZrwSJzPquTk0Q')

    dispatcher = updater.dispatcher
    #Cria o comando para o Bot
    dispatcher.add_handler(
        CommandHandler('address', localizacao)
    )
    dispatcher.add_handler(
        CommandHandler('rules', regras)
    )
    dispatcher.add_handler(
        CommandHandler('help', help)
    )

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
