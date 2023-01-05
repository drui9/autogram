from autogram.updates import Message
from autogram import Autogram, load_config

@Message.addAdminHandler
def adminHandler(message: Message):
    message.replyText('command-mode')

@Message.addHandler
def guestHandler(message: Message):
    message.replyText("Guest, welcome!")


if __name__ == '__main__':
    bot = Autogram(config = load_config())
    bot_thread = bot.send_online()
    bot_thread.join()
