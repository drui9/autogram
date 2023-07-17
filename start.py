from requests.exceptions import ConnectionError
from autogram import Autogram
from autogram import Start
from loguru import logger


@Start()
def main(config):
    bot = Autogram(config)
    try:
        bot.start()
    except ConnectionError:
        bot.logger.critical('Connection Error!')
    except Exception as e:
        bot.logger.exception(e)
    finally:
        bot.terminate.set()
