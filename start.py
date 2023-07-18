from autogram import Autogram
from autogram import Start
from loguru import logger

def handle_update(update):
    logger.info(update)

@Start()
def main(config):
    bot = Autogram(config)
    # bot.settings('AUTOGRAM_ENDPOINT', 'https://3c23-105-161-113-44.ngrok.io') # example webhook addr injection
    bot.addHandler(handle_update)
    bot.start()
