import os
import loguru
from autogram.base import Bot
from autogram.models import *
from requests.exceptions import ConnectionError


class Autogram(Bot):
  def __init__(self, config) -> None:
    """Initialize super, then database metadata respectively"""
    super().__init__(config)
    return

  def prepare(self):
    """Confirm auth through getMe(), then check update methods"""
    res = self.getMe()
    if not res.ok:
      self.do_err(msg=str(res.json()))
    self.webhook_addr = self.config.get('AUTOGRAM_ENDPOINT') or os.getenv('AUTOGRAM_ENDPOINT')
    if self.webhook_addr:
      res = self.setWebhook(self.webhook_addr)
      if not res.ok:
        self.do_err(msg='/setWebhook failed!')
    else:
      res = self.deleteWebhook()
      if not res.ok:
        self.do_err('/deleteWebhook failed!')
      else:
        self.short_poll()
    return

  def start(self):
    """Launch the bot"""
    try:
      self.prepare()
      self.terminate.wait(timeout=10)
    except ConnectionError:
      self.terminate.set()
      self.logger.critical('Connection Error!')
    finally:
      self.shutdown()

  def shutdown(self):
    """Gracefully terminate the bot"""
    if self.terminate.is_set():
      try:
        res = self.getWebhookInfo()
        if not res.ok:
          return
        if not res.json()['result']['url']:
          return
      except:
        return
    # delete webhook and exit
    try:
      res = self.deleteWebhook()
      if not res.ok:
        raise RuntimeError()
    except Exception as e:
      self.logger.critical('/deleteWebhook failed!')
    finally:
      self.terminate.set()
