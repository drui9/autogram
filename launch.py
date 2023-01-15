import os
from autogram.updates import Message
from autogram import Autogram, onStart

@Message.onCommand('start')
def commandHandler(msg: Message):
    msg.delete()
    msg.textBack(f"Hi, {msg.sender['first_name']} {msg.sender['last_name']}!",  parse_mode = 'MarkdownV2')

@Message.onCommand('shutdown')
def shutdownCommand(msg: Message):
    msg.autogram.terminate.set()
    msg.delete()

@Message.onMessageType('text')
def messageHandler(msg: Message):
    msg.textBack(msg.text)

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
    msg.delete()

@onStart('autogram.json')
def startBot(config: dict):
    bot = Autogram(config=config)
    print(Message.getCommands())
    bot_thread = bot.send_online()
    bot_thread.join()

