"""
@author: drui9
@config values:
    - update-endpoint: optional
    - ngrok-token: optional
    - bot-token: required
    - cava-auth: optional
"""
import os
import requests
from unittest import mock
from autogram import Autogram
from dotenv import load_dotenv
from autogram.config import load_config

def get_update_endpoint(validator_fn, inject_key=None):
    """Get updates endpoint, silently default to telegram servers"""
    if key := os.getenv('ngrok-api-key', inject_key):
        header = {'Authorization': f'Bearer {key}', 'Ngrok-Version': '2'}
        try:
            def getter():
                if os.getenv('TESTING') == '1':
                    return 'http://localhost:8000'
                rep = requests.get('https://api.ngrok.com/tunnels', headers=header, timeout=6)
                if rep.ok and (out := validator_fn(rep.json())):
                    return out
            return getter
        except Exception:
            raise
    return Autogram.api_endpoint

# modify to select one ngrok tunnel from list of tunnels
def select_tunnel(tunnels):
    for tunnel in tunnels['tunnels']:
        if tunnel['forwards_to'] == 'http://api:8000':
            return tunnel['public_url']

# launcher
if __name__ == '__main__':
    load_dotenv()
    config = Autogram.cfg_template()
    with load_config(config):
        if ngrok_token := config.get('ngrok-token'):
            if getter := get_update_endpoint(select_tunnel, ngrok_token):
                config['update-endpoint'] = getter()
                bot = Autogram(config)
                bot.getter = getter # fn to get updated endpoint
                bot.loop()

