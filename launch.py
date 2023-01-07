from autogram.updates import Message
from autogram import Autogram, load_config

@Message.onCommand('/start')
def commandHandler(msg: Message):
    msg.deleteMessage()
    msg.sendText("Hello! How may I help you?")

@Message.onCommand('/logout')
def stopHandler(msg: Message):
    msg.deleteMessage()
    if msg.autogram.admin == msg.sender['id']:
        msg.autogram.admin = None
    else:
        msg.autogram.deputy_admin = None
    msg.sendText('Logged out.')

@Message.onCommand('/shutdown')
def shutdownCommand(msg: Message):
    msg.autogram.terminate.set()
    msg.deleteMessage()

@Message.onMessageType('text')
def messageHandler(msg: Message):
    msg.replyText(msg.text)


if __name__ == '__main__':
    bot = Autogram(config = load_config())
    bot_thread = bot.send_online()
    try:
        bot_thread.join()
    except:
        print('>> out of context <<')
        raise
