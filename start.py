from autogram import Autogram
from autogram.config import load_config, Start

#--
@Start(config_file='web-auto.json')
def main(config):
    bot = Autogram(config)
    bot.start()
