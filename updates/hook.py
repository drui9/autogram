from autogram.autogram import Autogram


class WebHook:
    def __init__(self, url):
        self.url = url
        print('Webhook initialized.')

    def init_bot(self, instance :Autogram):
        print(instance)