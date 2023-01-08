<p style="text-align: center;">
    <img src="https://github.com/sp3rtah/autogram/blob/main/autogram.png" align="middle" alt="Autogram">
<p>

# An efficient asyncronous Telegram bot API wrapper!
Autogram is an asyncrounous, extensible telegram BOT API wrapper written in python using asyncio. 

```python
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
```
The above implementation assumes you want to control your bot through telegram messages only, as calling join on `bot.send_online(...)` which returns a thread object will block. If you intend to use the bot alongside other code, call `bot.send_online(...)` and leave it at that. The bot thread will terminate when your program finishes execution. 
1. You can use the bot handle returned by `bot = Autogram(token)` to terminate the telegram bot. Just call `bot.terminate.set()` to set the terminate event in the bot thread.
2. The bot has implicit chat actions. i.e typing, sending photo, etc which are invoked when you call reply functions on update objects.

## Why AutoGram?
I needed a bot framework that was easy to control remotely.

AutoGram has a built-in webhook endpoint written using Bottle Framework. Therefore, if you have a public IP, or can get an external service to comminicate with `localhost` through a service like ngrok (I use it too!), then add that IP or publicly visible address to your environment variables. If the public addr is not found, the program will use polling to fetch updates from telegram servers.
You add functionality to Autogram bot py implementing and adding callback functions. The bot will therefore work with available callbacks, and will continue to work even if none is specified! This allows the bot to work with available features, despite of missing handlers for specific types of messages.


# Tell me about the `callback` functions :)
The basic idea is that you can have a running bot without handlers. To be able to handle a normal user message, you'll need to import the `Message` module, and add a handler to it. When a normal user message is received, the Message object will parse the message, parse some of the content and set attributes on itself, then pass itself down to your handler. While creating the handler, you can tell the `Message` object whether you want to download message attachments too. If you don't, they will be downloaded when you attempt to access them. Below is a list of Update Objects you can (or will be able to) add callbacks to.

```python
from .poll import Poll, pollAnswer
from .message import Message, editedMessage
from .inline import inlineQuery, chosenInlineResult
from .channel import channelPost, editedChannelPost
from .chat import chatMember, myChatMember, chatJoinRequest
from .query import callbackQuery, shippingQuery, precheckoutQuery
```

The above are largely unimplemented, as my current project only requires the Message functionality. I intend to implement the rest either for fun, or as requirements for my future projects. Should you need an implementation, let me know so I can speed it up for you. I will include a list of completed features at the end.

# Complete Update types
- Message

## Upcoming features
- Bot will know it's admin. Errors or updates with unimplemented callbacks can be optionally forwarded to `admin` -> Done
- Better handling of message attachments    -> Implicitly forwarded to admin, if callback is not defined
- Plans to cover the entire telegram API -> in progress
- Format and forward notifications/alerts to admin. i.e: added to group, blocked, etc -> Not started

### footnotes
- short-polling is available for testing.
- If you're using with ngrok, use `ngrok http 4004`
- Don't run multiple bots with the same `TELEGRAM_TOKEN` as this will cause update problems
- Try and have fun ;)
