<p style="text-align: center;">
    <img src="https://raw.githubusercontent.com/drui9/autogram/main/autogram.png" align="middle" alt="Autogram">
<p>

## Installation :: 
`pip install autogram`
Autogram is a telegram-BOT API wrapper written in python3, with a keen focus on remaining stupidly simple.

## `Why AutoGram?`
The name implies automated-telegram. I needed a framework that is easy and intuitive to work with.

## Usage
```python
from autogram import Autogram
from autogram.config import load_config, Start

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
You should implement a loop over `bot.run()` to fetch updates inside your application. This makes the timing arbitrary, depending on where the program is expected to run. i.e offline gadgets that do not have consistent internet to use a webhook, or a server(with all the incredible webhook features using public IP/ngrok or custom domain name and a possibility of a HTTPS nginx endpoint).

## `Project TODOs`
- Tests.
- Add webhook support.
- Plans to cover the entire telegram API methods.

### `footnotes`
- `Polling` is the default getUpdates() method.
- Don't run multiple bots with the same `TOKEN` as this will cause update problems
- Sending unescaped special characters when using MarkdownV2 will return HTTP400
- Have `fun` with whatever you're building `;)`
