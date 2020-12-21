from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackContext
from telegram import Update, Bot, Document
import requests as re
import os
import glob

#Colocar aqui o token do seu BOT
token = ''
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

# POSSIVEIS ERROS:
#Secção criada para que, caso o usuário escreva um comando comando errado
#Ou tente conversar com o Bot

def comando_Errado(update: Update, context: CallbackContext):
    resposta = "Esse comando não existe. Favor checar a digitação!"
    update.message.reply_text(resposta)

def conversa_paralela(update: Update, context: CallbackContext):
    resposta = "Sou um Robô!!!, não tenho assunto. Favor utilizar os comandos!"
    update.message.reply_text(resposta)

#COMANDOS DINAMICOS:

#Newsletter, puxa o arquivo do folder 'news' e envia pela API
def newsletter(bot, update):
    try:
        #Procura o arquivo mais novo presente
        mais_novo_arquivo = max(glob.iglob('news/*.pdf'), key=os.path.getctime)
        documento = {'document': open(mais_novo_arquivo, 'rb')}
        resp = re.post('https://api.telegram.org/bot{}/sendDocument?chat_id={}'.format(token,update.message.chat_id), files = documento)
    #Caso não tenha arquivo, ou o nome está errado:
    except FileNotFoundError:
        print("Esse arquivo não existe, favor checar a pasta!")
        update.message.reply_text("Estamos sem arquivos, favor contactar a Diretoria do HS")


def main():
    #Esse updater puxa nosso bot da API do telegram, esse token
    #é entregue quando criamos o bot.
    updater = Updater(token = token, use_context = False)

    dispatcher = updater.dispatcher
    #Cria o comando para o Bot
    #COMANDOS ESTATICOS
    dispatcher.add_handler(
        CommandHandler('address', localizacao)
    )
    dispatcher.add_handler(
        CommandHandler('rules', regras)
    )
    dispatcher.add_handler(
        CommandHandler('help', help)
    )
    #COMANDOS DINAMICOS
    dispatcher.add_handler(
        CommandHandler('news', newsletter)
    )
    #Faz o bot receber a mensagem e processar uma resposta
    dispatcher.add_handler(
        #filters filtrará o que foi especificado
        MessageHandler(Filters.command, comando_Errado)
    )
    dispatcher.add_handler(
        #filters filtrará o que foi especificado
        MessageHandler(Filters.all, conversa_paralela)
    )

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
