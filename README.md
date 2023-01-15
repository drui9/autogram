<p style="text-align: center;">
    <img src="https://raw.githubusercontent.com/sp3rtah/autogram/main/autogram.png" align="middle" alt="Autogram">
<p>

# 0x00 An efficient asyncronous Telegram bot API wrapper!
Autogram is an easily extensible telegram BOT API wrapper that uses aiohttp to disparch requests. Get ahead quickly by simply cloning and adding new callbacks to this module!
```python
import os
from autogram.updates import Message
from autogram import Autogram, onStart


@Message.onCommand('/start')
def commandHandler(msg: Message):
    msg.deleteMessage()
    msg.sendText("Hello! How may I help you?")
    return

@Message.onCommand('/shutdown')
def shutdownCommand(msg: Message):
    msg.autogram.terminate.set()
    msg.deleteMessage()
    return

# echo texts
@Message.onMessageType('text')
def messageHandler(msg: Message):
    msg.replyText(msg.text)
    return

# save non-text messages to ./Downloads
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
    return

@onStart('autogram.json')
def startBot(config: dict):
    bot = Autogram(config=config)
    bot_thread = bot.send_online()
    bot_thread.join()
```

The above implementation assumes you want to control your bot through telegram messages only, as calling join on `bot.send_online(...)` which returns a thread object will block. If you intend to use the bot alongside other code, call `bot.send_online(...)` and leave it at that. The bot thread will terminate when your program finishes execution. 
1. You can use the bot handle returned by `bot = Autogram(token)` to terminate the telegram bot. Just call `bot.terminate.set()` to set the terminate event in the bot thread.
2. The bot has implicit chat actions. i.e typing, sending photo, etc which are invoked when you call reply functions on update objects.

# 0x02 Why AutoGram?
I needed a bot framework that was easy to control remotely.

AutoGram has a built-in webhook endpoint written using Bottle Framework. Therefore, if you have a public IP, or can get an external service to comminicate with `localhost` through a service like ngrok (I use it too!), then add that IP or publicly visible address to your environment variables. If the public addr is not found, the program will use polling to fetch updates from telegram servers.
You add functionality to Autogram bot py implementing and adding callback functions. The bot will therefore work with available callbacks, and will continue to work even if none is specified! This allows the bot to work with available features, despite of missing handlers for specific types of messages.

# 0x03 Tell me about the `callback` functions :)
The basic idea is that you can have a running bot without handlers. To be able to handle a normal user message, you'll need to import the `Message` module, and add a handler to it. When a normal user message is received, the Message object will parse the message, parse some of the content and set attributes on itself, then pass itself down to your handler. While creating the handler, you can tell the `Message` object whether you want to download message attachments too. If you don't, they will be downloaded when you attempt to access them. Below is a list of Update Objects you can (or will be able to) add callbacks to.
```python
from .poll import Poll, pollAnswer
from .message import Message, editedMessage
from .inline import inlineQuery, chosenInlineResult
from .channel import channelPost, editedChannelPost
from .chat import chatMember, myChatMember, chatJoinRequest
from .query import callbackQuery, shippingQuery, precheckoutQuery
```
# 0x04 Currently implemented update types
- Message

# 0x06 Upcoming features
- Plans to cover the entire telegram API
- Add onDisconnect and onNotification
- Add a background ngrok server if ngrok is in path, and no public ip
- Make `retry` default behaviour, customizable with onDisconnect callback.

# ChangeLog
- Removed admin and deputy functionalities
- Autogram has a reusable ThreadPoolExecutor using a .toThread(*args) method
- Added onStart(*args) handler which can be used to start the bot.

# Deprecated features
- Default behaviour is to forward messages to admin.
- Admin can have an assistant.

### `footnotes`
- short-polling is available for testing.
- If you're using with ngrok, use `ngrok http <tcp-port>`
- Don't run multiple bots with the same `TELEGRAM TOKEN` as this will cause update problems
- Have fun with whatever you're building ;)

