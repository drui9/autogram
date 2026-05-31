# autogram
An easily extensible telegram API wrapper
Autogram is a telegram bot-API wrapper written in python3, with a keen focus on remaining stupidly simple.

## QuickStart
pip install autogram

### Why AutoGram?
The name implies automated-telegram.
An easy and intuitive frameworm to start with.

### Usage1: Functional
```python
from autogram import Autogram
from autogram.config import Start

#-- handle private dm
@Autogram.add('message')
def message(bot, update):
    print('message:', update)

#-- handle callback queries
@Autogram.add('callback_query')
def callback_query(bot, update):
    print('callback_query:', update)

#***************************** <start>
@Start(config_file='web-auto.json')
def main(config):
    bot = Autogram(config)
    bot.run() # every call fetches updates, and updates internal offset
#-- </start>
```

### Usage2: OOP
```python
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
@Start()
def main(config):
    bot = ExampleBot(config)
    bot.run()
# ************ </start>
```
