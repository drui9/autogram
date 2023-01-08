import os
import sys
import json
from dotenv import load_dotenv

default_config = {
    'tcp_timeout': 6,
    'max_retries': 7,
    'admin_username': None,
    'contingency_pwd': None,
    'public_ip': None,
    'telegram_token': None,
}

def load_config():
    load_dotenv()
    # check if config file exists
    config_file = os.getenv('CONFIG_FILE')
    if not config_file:
        raise RuntimeError('No config file defined in environment!')

    if not os.path.exists(config_file):
        with open(config_file, 'w') as conf:
            json.dump(default_config, conf, indent=3)
        print(f"Please edit [{config_file}]")
        sys.exit(1)
    with open(config_file, 'r') as conf:
        return json.load(conf)

__all__ = [
    'load_config',
    'default_config'
]
