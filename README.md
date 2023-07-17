<p style="text-align: center;">
    <img src="https://raw.githubusercontent.com/sp3rtah/autogram/main/autogram.png" align="middle" alt="Autogram">
<p>

## `0x00 An efficient asyncronous Telegram bot API wrapper!`
Autogram is a telegram BOT API wrapper with focus on simplicity and performance.

## `0x01 Why AutoGram?`
I need a bot framework that makes it easy to administer control remotely.

Autogram has a built-in webhook endpoint written using Bottle. Therefore, if you have a public IP, or can get an external service to comminicate with `localhost` through a service like ngrok (I use it too!), then set that endpoint as AUTOGRAM_ENDPOINT in your environment variable, or inject its value in the bot config during startup. If the public address provided is not accessible, the program will use polling to fetch updates. If the telegram token is missing in config file, or is invalid, the bot will terminate.
You add functionality to Autogram bot py implementing and adding callback functions. The bot will therefore work with available callbacks, and will continue to work even if none is specified! This allows the bot to work with available features, despite of missing handlers for specific types of messages.

## `0x02 Currently implemented update types`
- todo: re-implementing

## `0x03 Upcoming features`
- Add onNotification handlers.
- Plans to cover the entire telegram API.
- Escape special characters internally.

### `footnotes`
- `Polling` can be implemented by the user, while feeding data to the bot through `bot.parseUpdate(...)`
- Autogram searches for bot `token` in the specified `config file` before resolving to env variable value.
- Don't run multiple bots with the same `TOKEN` as this will cause update problems
- Sending unescaped special characters when using MarkdownV2 will return HTTP400
- Have `fun` with whatever you're building `;)`
