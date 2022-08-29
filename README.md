<p style="text-align: center;">
    <img src="./autogram.png" align="middle" alt="Autogram logo">
<p>

# An efficient asyncronous Telegram bot API wrapper!
Autogram is an asyncrounous `configure and forget` telegram BOT API wrapper written in python using asyncio coroutine framework. 

```python
import os
from dotenv import load_dotenv

from autogram import Autogram
from autogram.updates.message import Message

@Message.addHandler
def textHandler(message: Message):
    print(message)
    message.replyText('I received your message!')

def main():
    public_addr = os.getenv('PUBLIC_URL')  # pubic ip, or ngrok addr
    token = os.getenv('TELEGRAM_TOKEN') # from BotFather
    bot = Autogram(token)   # get handle to the bot
    bot.send_online(pub_addr).join()  # bot runs in separate thread.

if __name__ == '__main__':
    load_dotenv()
    main()

```
See! :)

The above implementation assumes you want to control your bot through telegram messages only, as calling join on `bot.send_online(...)` which returns a thread object will block. If you intend to use the bot alongside other code, call `bot.send_online(...)` and leave it at that. The bot thread will terminate when your program finishes execution. 

A couple things you'd wish to know beforehand:
1. When the internet connection is poor, the bot will retry contacting the server 12 times. Should all the 12 calls fail, the bot will terminate. Note that when using a webhook, these calls will be made during setup stage, as we'll be waiting for telegram to send messages to us most of the time. Internal functionality may make calls periodically too. This will be clarified at a later stage.

2. You can use the bot handle returned by `bot = Autogram(token)` to terminate the telegram bot. Just call `bot.terminate.set()` to set the terminate event in the bot thread.

3. You really wanna make sure your bot is accessible by telegram. From their documentation, telegram will try accessing your webhook endpoint whenever there's pending updates, and stop after a reasonable number of attempts should your service be inacessible. Outgoing calls from the bot can detect this, but in their absence, there's no way for the bot to know if there's a network issue.

4. The bot has implicit chat actions. i.e typing, sending photo, etc which are invoked when you call reply functions on update objects.

## Upcoming features
- Bot will know it's admin. Errors or updates with unimplemented callbacks can be optionally forwarded to `admin`
- Better handling of message attachments
- Plans to cover the entire telegram API

## Why AutoGram?
I looked around for a reliable wrapper for use in my projects but found none was to my taste. You might have come across teleBot -a prototype that's also public here on github- which essentially is the backbone of this async version. 


# What's the difference between teleBot and Autogram?
I wrote teleBot to better understand the telegram bot API. I used it in Poetry -A telegram bot that replies with poems based on themes you send it. It works for it's purpose, but developers have to handle everything including fetching updates, or setting webhooks. The wrapper has functionality for working with attachments like media and files, but the developer has to explicitly direct the wrapper logic. 

As for AutoGram, the bot is asyncronous, and runs in a separate daemon thread. If used in a larger application, the bot terminates when the 'main' program terminates. Alternatively, you can join on the bot thread if termination functionality is included in the `callback` functions. Especially in cases where the telegram bot is the main application.

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

# Notice:
    This project is still in it's conseptual stage, and I take my time to come up with ideal ways I'd want users to consume the API. Simplicity and consistency are what I aim for. I wrote this for personal use as existing wrappers were either too verborse or had a steep learning curve, or both. I tend to delete, upgrade or make private my opensource projects without backward compatibility, especially if they're unutilised .So feel free to use this library in whatever usecase you may have, but do me one favor: Let me know. Maybe you're the reason this project stays public. :)


# Working Features with examples of adding handlers
- Message
- More coming soon...

```python
from autogram.updates.message import Message

@Message.addHandler
def textHandler(message: Message):
    print(message)
```


### footnotes
- I use [launch.py](launch.py) for in-development testing. It might give you an insight on how this useful wrapper can be used!
- Don't run multiple bots with the same `TELEGRAM_TOKEN` as this will cause update problems
- If you're using with ngrok, the bot webhook runs on port 4004
- Only use long/short-polling for testing.
- Try and have fun. Life's already depressing as it is.(No? it is to me) ;)
