import os
from autogram import Autogram
from autogram.updates.message import Message
from dotenv import load_dotenv

load_dotenv()

@Message.addHandler
def textHandler(message: Message):
    print(message.attachments)


if __name__ == '__main__':
    pub_addr = os.getenv('PUBLIC_URL') or ''
    token = os.getenv('TELEGRAM_TOKEN') or ''
    if not token:
        raise RuntimeError('Telegram token not in environment')
    bot = Autogram(token)
    bot_thread = bot.send_online(pub_addr)
    bot_thread.join()