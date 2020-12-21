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

def localizacao(bot, update):
    #Escrevemos o texto que o bot irá mandar
    resposta = "R. Vitória, 943 - Vila Esperanca, Maringá - PR"
    bot.send_message(
        chat_id=update.message.chat_id,
        text=resposta
    )

def regras(bot, update):
    resposta = "Colocar texto aqui"
    bot.send_message(
        chat_id=update.message.chat_id,
        text=resposta
    )

def help(bot, update):
    resposta = "Colocar texto aqui"
    bot.send_message(
        chat_id=update.message.chat_id,
        text=resposta
    )

# POSSIVEIS ERROS:
#Secção criada para que, caso o usuário escreva um comando comando errado
#Ou tente conversar com o Bot

def comando_Errado(bot, update):
    resposta = "Esse comando não existe. Favor checar a digitação!"
    bot.send_message(
        chat_id=update.message.chat_id,
        text=resposta
    )

def conversa_paralela(bot, update):
    resposta = "Sou um Robô!!!, não tenho assunto. Favor utilizar os comandos!"
    bot.send_message(
        chat_id=update.message.chat_id,
        text=resposta
    )

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
        bot.send_message(
            chat_id=update.message.chat_id,
            text=resposta
        )


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
