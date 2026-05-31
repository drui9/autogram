import time
from loguru import logger
from threading import Event
from autogram import Autogram, Start

# --
class ExampleBot(Autogram):
    def __init__(self, config):
        super().__init__(config)

    def run(self):
        """Override super().run implementation"""
        super().run() # initializes bot info, abstractmethod
        while not self.stop:
            offset = self.data('offset')
            for rep in self.poll(offset=offset).json()['result']:
              self.data('offset', rep.pop('update_id') + 1)
              with self.register['lock']:
                if handler := self.register['handlers'].get(list(rep.keys())[-1]):
                  handler(self, self, rep)
            time.sleep(5)

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
@Start(config_file='autogram.json')
def main(config):
    bot = ExampleBot(config)
    bot.run()
# ************ </start>
