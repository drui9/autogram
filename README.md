<p style="text-align: center;">
    <img src="https://raw.githubusercontent.com/drui9/autogram/main/autogram.png" align="middle" alt="Autogram">
<p>

Autogram is a telegram bot-API wrapper written in python3, with a keen focus on remaining stupidly simple.

## QuickStart
`pip install autogram`
- Copy either the Functional or OOP example below.
- Run the bot the first time to generate `project-name.json` config template
- Add your telegram bot token in the config, (from telegram:BotFather chat)
- Ready to run.
- Add your own logic and handler methods. `core.telegram.org` manual is your friend.

## `Why AutoGram?`
The name implies automated-telegram. I needed a framework that is easy and intuitive to work with.

## Usage1: Functional
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
## Usage2: OOP
```python
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
If you have a url-endpoint, call bot.setWebhook(url), then run some sort of webserver in bot.run.

## `Project TODOs`
- Add webhook example.
- Extend coverage of the API.

### `footnotes`
- Invalid `TELEGRAM_TOKEN` return 404 through `bot.getMe()`
- Thread safety is not guaranteed for calls from multiple threads to: `bot.data, bot.settings`. Prefferably, handle the bot in a single thread, as handlers use these methods to persist data.
- Don't run multiple bots with the same `TOKEN` as this will cause update problems
- Sending unescaped special characters when using MarkdownV2 will return HTTP400
- Have `fun` with whatever you're building `;)`

