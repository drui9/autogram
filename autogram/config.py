import os
import sys
import json
from typing import Callable


default_config = {
    'tcp_timeout': 6,
    'max_retries': 7,
    'admin_username': None,
    'contingency_pwd': None,
    'public_ip': None,
    'telegram_token': None,
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
        return json.load(conf)


def onLoadConfig(conf = 'autogram.json', confpath = '.'):
    """Call external function when config is loaded"""
    def wrapper(onLoadCallback: Callable):
        return onLoadCallback(load_config(conf, confpath))
    return wrapper


__all__ = [ 'onLoadConfig' ]
