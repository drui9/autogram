from autogram.updates import Message
from autogram import Autogram, load_config


@Message.addHandler
def textHandler(message: Message):
    message.replyText(message.attachments['text'])


if __name__ == '__main__':
    bot = Autogram(config = load_config())
    bot_thread = bot.send_online()
    bot_thread.join()