from autogram import Autogram
from autogram.config import load_config, Start

#--
@Autogram.add('message')
def message(bot, update):
    print('message:', update)

#--
@Autogram.add('edited_message')
def edited_message(bot, update):
    print('edited_message:', update)

#--
@Autogram.add('channel_post')
def channel_post(bot, update):
    print('channel_post:', update)

#--
@Autogram.add('edited_channel_post')
def edited_channel_post(bot, update):
    print('edited_channel_post:', update)

#--
@Autogram.add('callback_query')
def callback_query(bot, update):
    print('callback_query:', update)

#--
@Autogram.add('message_reaction')
def message_reaction(bot, update):
    print('message_reaction:', update)

#--
@Autogram.add('message_reaction_count')
def message_reaction_count(bot, update):
    print('message_reaction_count:', update)

#--
@Autogram.add('chat_member')
def chat_member(bot, update):
    print('chat_member:', update)

#--
@Autogram.add('my_chat_member')
def my_chat_member(bot, update):
    print('my_chat_member:', update)

#--
@Autogram.add('chat_join_request')
def chat_join_request(bot, update):
    print('chat_join_request:', update)

#***************************** <start>
@Start(config_file='web-auto.json')
def main(config):
    bot = Autogram(config)
    bot.run()
#-- </start>