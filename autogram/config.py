import os
import sys
import json
from loguru import logger
from typing import Callable, Dict

default_config = {
    'tcp-port': 4004,
    'tcp-ip': 'ngrok',
    'tcp-timeout': 10,
    'max-workers': 32,
    'echo-responses': False,
    'media-quality': 'high',
    'telegram-token': None,
}

@logger.catch
def load_config(config_file : str, config_path : str):
    """Load configuration file from config_path dir"""
    if not os.path.exists(config_path):
        os.mkdir(config_path)
    #
    config_file = os.path.join(config_path, config_file)
    if not os.path.exists(config_file):
        with open(config_file, 'w') as conf:
            json.dump(default_config, conf, indent=3)
        print(f"Please edit [{config_file}]")
        sys.exit(1)
    config = {'config-file': config_file}
    with open(config_file, 'r') as conf:
        config |= json.load(conf)
    return config

@logger.catch
def save_config(config :Dict):
    """config-file must be in the dictionary"""
    if config.get('config-file'):
        conffile = config.pop('config-file')
        with open(conffile, 'w') as conf:
            json.dump(config, conf, indent=3)
            conf.flush()
        return True
    return False

@logger.catch
def onStart(conf = 'autogram.json', confpath = '.'):
    """Call custom function with config as parameter"""
    def wrapper(func: Callable):
        return func(load_config(conf, confpath))
    return wrapper
#

__all__ = [ "onStart", "save_config", "load_config"]

