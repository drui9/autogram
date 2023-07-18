# from autogram import Autogram
# from autogram import Start
# from loguru import logger


# @Start()
# def main(config):
#     bot = Autogram(config)
#     # bot.settings('AUTOGRAM_ENDPOINT', 'https://3c23-105-161-113-44.ngrok.io') # example webhook addr injection
#     bot.start()

""" Test database functionalities """
import json
from autogram.models import *
from sqlalchemy.orm import Session

the_update = {
    "message":
        {
            "message_id": 18,
            "from":
            {
                "id": 5342492667,
                "is_bot": False,
                "first_name": "Druid",
                "username": "sp3rtah",
                "language_code": "en"
            },
            "chat":
            {
                "id": 5342492667,
                "first_name": "Druid",
                "username": "sp3rtah",
                "type": "private"
            },
            "date": 1689592717,
            "text": "/start",
            "entities":
            [
                {
                    "offset": 0,
                    "length": 6,
                    "type": "bot_command"
                }
            ]
        }
    }

def main():
    bot = BotBase()
    bot.id = 6372449397
    bot.first_name = "Dru's"
    bot.username = "drus001_bot"
    bot.can_join_groups = True

    update = Update()
    update.id = 832528793
    update.date = 1689592717
    update.data = json.dumps(the_update)
    update.bot = bot

    update2 = Update()
    update2.id = 832528794
    update2.date = 1689592717
    update2.data = json.dumps(the_update)
    update2.bot = bot

    with Session(bind=bot.engine) as session:
        session.add(bot)
        session.commit()
    with Session(bind=bot.engine) as session:
        thebot = session.query(BotBase).first()
        theupdates = session.query(Update).filter_by(bot=thebot).count()
        print(theupdates)



main()
print('--end--')
