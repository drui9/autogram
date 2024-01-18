from updates import endpoint, terminate, logger
from autogram.autogram import Autogram
from datetime import datetime
import threading
import requests
import time
import json


class ShortPoll:
    def __init__(self, interval=7):
        self.url = endpoint
        self.interval = max(7, interval)

    def init_bot(self, instance :Autogram) -> bool:
        link = self.url + f'bot{instance.token}/getMe'
        rep = requests.get(link, timeout=10)
        if rep.ok:
            instance.terminate = terminate
            instance.info = json.loads(rep.content.decode('utf8'))
            return self.start(instance)
        raise RuntimeError(rep.content)
    
    def start(self, bot : Autogram):
        t = threading.Thread(target=bot.start)
        t.name = 'Autogram'
        t.start()
        # configure update source
        link = self.url + f'bot{bot.token}/getUpdates'
        def getUpdates():
            #<do_get>
            def do_get(prev_update):
                try:
                    headers = {
                        'offset': prev_update['id']
                    }
                    rep = requests.get(link, params=headers, timeout=5)
                    if not rep.ok:
                        raise RuntimeError(rep.content.decode('utf8'))
                    updates = json.loads(rep.content.decode('utf8'))['result']
                    for update in updates:
                        bot.updates.put(update)
                        if prev_update['id'] <= (theid := update['update_id']):
                            prev_update['id'] = theid + 1
                            prev_update['time'] = time.time()
                            logger.info(f'Updated at: {datetime.fromtimestamp(prev_update["time"])}')
                except Exception as e:
                    logger.critical(e)
            #<do_get/>
            prev_update = {
                'id': 0,
                'time': time.time()
            }
            while not terminate.is_set():
                the_get = threading.Timer(3, do_get, (prev_update,))
                the_get.start()
                the_get.join()
        return getUpdates()
