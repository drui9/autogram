from autogram import Autogram
from autogram import Start
from loguru import logger


@Start()
def main(config):
    bot = Autogram(config)
    config.update({'AUTOGRAM_ENDPOINT': 'https://2f8c-105-161-113-44.ngrok.io'})
    bot.start()
