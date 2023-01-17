<p style="text-align: center;">
    <img src="https://raw.githubusercontent.com/sp3rtah/autogram/main/autogram.png" align="middle" alt="Autogram">
<p>

## 0x00 An efficient asyncronous Telegram bot API wrapper!
Autogram is an easily extensible telegram BOT API wrapper. You can get to work quickly by simply cloning this repository and adding custom callbacks to launch.py in root directory!

```python
import os
from autogram.updates import Message
from autogram import Autogram, onStart

# bot commands        
@Message.onCommand('start')
def commandHandler(msg: Message):
    msg.delete()
    msg.sendText(
        f"*Defined Commands*\n```python\n{msg.getCommands()}```",
        parse_mode='MarkdownV2'
    )

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
    bot_thread = bot.send_online()
    bot_thread.join() # optional. Bot terminates if main program exits
```

The above implementation assumes you want to control your bot through telegram messages only, as calling join on `bot.send_online(...)` which returns a thread object will block. If you intend to use the bot alongside other code, call `bot.send_online(...)` and leave it at that. The bot thread will terminate when your program finishes execution. 
1. You can use the bot handle returned by `bot = Autogram(config=config)` to terminate the telegram bot. Just call `bot.terminate.set()` from your thread to set the termination flag.
2. The bot has implicit chat actions. i.e typing, sending photo, etc which are invoked when you call reply functions on update objects.

## 0x02 Why AutoGram?
I needed a bot framework that was easy to control remotely.

AutoGram has a built-in webhook endpoint written using Bottle Framework. Therefore, if you have a public IP, or can get an external service to comminicate with `localhost` through a service like ngrok (I use it too!), then add that IP or publicly visible address to your environment variables. If the public addr is not found, the program will use polling to fetch updates from telegram servers.
You add functionality to Autogram bot py implementing and adding callback functions. The bot will therefore work with available callbacks, and will continue to work even if none is specified! This allows the bot to work with available features, despite of missing handlers for specific types of messages.

The basic idea is that you can have a running bot without handlers. To be able to handle a normal user message, you'll need to import the `Message` module, and add a handler to it. When a normal user message is received, the Message object will parse the message, parse some of the content and set attributes on itself, then pass itself down to your handler. While creating the handler, you can tell the `Message` object whether you want to download message attachments too. If you don't, they will be downloaded when you attempt to access them. Below is a list of Update Objects you can (or will be able to) add callbacks to.

## 0x03 Currently implemented update types
- Message

## 0x04 Upcoming features
- Add onNotification handlers
- Plans to cover the entire telegram API
- Wait on high-priority and io-tasks before shutdown with optional timeout.

## ChangeLog
- Added `ngrok-path` to config. Update to point to your installed version. if not found, it'll download.
- Added `io-tasks, high-priority and common-tasks` priority groups to threadpool workers. Do:
    ```python
    bot.toThread(max, 1, 2, priority='high-priority')
    bot.toThread(min, 1, 2, priority='common-tasks')
    bot.toThread(floor, 2.5, priority='io-tasks')

    """
    max, min and floor are example functions, whose arguments are the numbers.
    """
    ```
- Added a background ngrok server with pyngrok
- Added onStart(*args) handler which can be used to start the bot.
- Autogram has a reusable ThreadPoolExecutor using a .toThread(*args) method that takes kwarg which is a callbackfunction
- save_config and load_config available from Autogram. onStart calls load_config implicitly

## Deprecated features
- Admin and deputy functionalities
- Default behaviour is to forward messages to admin.
- Admin can have an assistant.

### `footnotes`
- short-polling and ngrok servers are available for testing.
- Don't run multiple bots with the same `TOKEN` as this will cause update problems
- Have `fun` with whatever you're building ;)

