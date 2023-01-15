import os
import sys
import json
from typing import Callable, Dict

default_config = {
    'env': 0, # {'dev': 0, 'production': 1}
    'tcp-port': 4004,
    'tcp-timeout': 10,
    'log-level': 'INFO',
    'media-quality': 'high',
    'telegram-token': None,
    'public-ip': None,
}

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
    with open(config_file, 'r') as conf:
        return json.load(conf) | {'config-file': config_file}

def save_config(config : Dict):
    """Save configuration file to config_path dir"""
    if config_file := config.get('config-file'):
        with open(config_file, 'w') as conf:
            json.dump(default_config, conf, indent=3)
            conf.flush()
            return True
    return False

def onStart(conf = 'autogram.json', confpath = '.'):
    """Call custom function with config as parameter"""
    def wrapper(func: Callable):
        return func(load_config(conf, confpath))
    return wrapper
#

__all__ = [ "onStart", "save_config", "load_config"]

