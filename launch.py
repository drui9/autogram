import os
from autogram import Autogram, onStart
from autogram.updates import Message, callbackQuery

@callbackQuery.addHandler
def callBackHandler(cb :callbackQuery):
    cb.answerCallbackQuery(text='Updated')
    cb.delete()

# bot commands        
@Message.onCommand('start')
def startCommand(msg: Message):
    msg.delete()
    msg.sendText(
        f"*Defined Commands*\n```python\n{msg.getCommands()}```",
        parse_mode='MarkdownV2',
        reply_markup = msg.autogram.getInlineKeyboardMarkup(
            [
                [{'text': 'Confirm', 'callback_data': 'confirmed'}]
            ],
            params = {
                'one_time_keyboard': True
            }
        )
    )

@Message.onCommand('shutdown')
def shutdownCommand(msg: Message):
    msg.delete()
    msg.sendText('Shutting down...')
    def exit_func(report:str):
        msg.logger.critical(report)
    msg.autogram.shutdown(exit_func)

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
    bot_thread = bot.send_online()
    bot_thread.join()

