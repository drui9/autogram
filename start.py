from autogram import Autogram
from autogram import Start
from loguru import logger
import requests


def get_tunnel(key):
    try:
        header = {'Authorization': f'Bearer {key}', 'Ngrok-Version': '2'}
        rep = requests.get('https://api.ngrok.com/tunnels', headers=header, timeout=10)
        if rep.ok:
            data = rep.json()
            if len(data['tunnels']) != 1:
                raise RuntimeError(data)
            return data['tunnels'][-1]
        raise RuntimeError(rep.content)
    except Exception:
        logger.exception('what?')
        raise

def handle_update(update):
    logger.info(update)

@Start()
def main(config):
    bot = Autogram(config)
    bot.addHandler(handle_update)
    if ngrok_key := config.get("NGROK_API_KEY"):
        try:
            tun = get_tunnel(ngrok_key)
            tun = tun['public_url']
        except Exception:
            logger.exception('what?')
        bot.settings("AUTOGRAM_ENDPOINT", tun)
    bot.start()
