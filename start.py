from autogram import Autogram
from autogram import Start
from loguru import logger


@Start()
@logger.catch
def main(config):
    bot = Autogram(config)
    bot.start()
