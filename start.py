from autogram.autogram import Autogram
from updates import ShortPoll
from dotenv import load_dotenv


if __name__ == '__main__':
    import os
    load_dotenv()
    poll = ShortPoll(interval=5)
    bot = Autogram(os.getenv('TELEGRAM-TOKEN'))
    poll.init_bot(bot)
