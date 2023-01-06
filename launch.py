from autogram.updates import Message
from autogram import Autogram, load_config


@Message.onCommandType('text')
def adminHandler(msg: Message):
    msg.replyText('Welcome!')

@Message.onMessageType('audio')
def guestHandler(msg: Message):
    audio = msg.getVideo('low')
    print(audio)

@Message.onMessageType('video')
def guestHandler(msg: Message):
    video = msg.getVideo('low')
    print(video)

@Message.onMessageType('photo')
def guestHandler(msg: Message):
    photo = msg.getPhoto('low')
    print(photo)

@Message.onMessageType('text')
def guestHandler(msg: Message):
    msg.replyText('Guest, welcome!')

if __name__ == '__main__':
    bot = Autogram(config = load_config())
    bot_thread = bot.send_online()
    try:
        bot_thread.join()
    except:
        print('>> out of context <<')
        raise
