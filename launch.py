import os
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

@Message.onMessageType('voice')
@Message.onMessageType('audio')
@Message.onMessageType('photo')
@Message.onMessageType('video')
@Message.onMessageType('document')
@Message.onMessageType('video_note')
def fileHandler(msg: Message):
    temp_dir = 'Downloads'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    file_path = f"{temp_dir}/{msg.file['name']}"
    with open(file_path, 'wb') as file:
        file.write(msg.file['bytes'])
    msg.deleteMessage()


if __name__ == '__main__':
    bot = Autogram(config = load_config())
    bot_thread = bot.send_online()
    ## do your own calls in this thread
    # main(bot)
    # join when done
    bot_thread.join()
