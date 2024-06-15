"""
@author: drui9
@description: Example usage
"""
import time
from loguru import logger
from autogram import Autogram, Start

# --
class ExampleBot(Autogram):
    def __init__(self, config):
        super().__init__(config)

    def run(self):
        """Custom implementation of bot.poll()"""
        super().run() # initializes bot info, abstractmethod
        for _ in range(10): # should be endless loop
            offset = self.data('offset') # fetch persisted offset
            for rep in self.poll(offset=offset).json()['result']:
              self.data('offset', rep.pop('update_id') + 1) # persist new offset
              with self.register['lock']: # ensure handlers are not modified during call
                if handler := self.register['handlers'].get(list(rep.keys())[-1]):
                    handler(self, self, rep) # call handler. Maybe try except?
            time.sleep(5) # not required for webhooks

    @Autogram.add('message')
    def message(self, bot: Autogram, update):
        logger.debug(update['message']['text'])
        chat_id = update['message']['chat']['id']
        keyb = [[{'text': 'The armpit', 'callback_data': 'tickled'}]]
        data = {
            'reply_markup': bot.getInlineKeyboardMarkup(keyb)
        }
        bot.sendMessage(chat_id, 'Tickle me!', **data)

    # --
    @Autogram.add('callback_query')
    def callback_query(self, bot: Autogram, update):
        callback_id = update['callback_query']['id']
        bot.answerCallbackQuery(callback_id, 'Ha-ha-ha')

#***************************** <start>
@Start()
def main(config):
    bot = ExampleBot(config)
    bot.run()
# ************ </start>
