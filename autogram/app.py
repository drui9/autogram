import os
import time
import queue
from autogram.base import Bot
from requests.exceptions import ConnectionError


class Autogram(Bot):
  def __init__(self, config) -> None:
    """Initialize parent object"""
    self.update_handler = None
    super().__init__(config)
    return

  def addHandler(self, function):
    self.update_handler = function
    return function

  def prepare(self):
    """Confirm auth through getMe(), then check update methods"""
    res = self.getMe()
    if not res.ok:
      self.do_err(msg=str(res.json()))
    self.webhook_addr = self.config.get('AUTOGRAM_ENDPOINT') or os.getenv('AUTOGRAM_ENDPOINT')  # noqa: E501
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
      while not self.terminate.is_set():
        try:
          if not self.update_handler:
            time.sleep(5)
            continue
          self.update_handler(self.updates.get())
        except queue.Empty:
          continue
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
      except Exception:
        return
    # delete webhook and exit
    try:
      res = self.deleteWebhook()
      if not res.ok:
        raise RuntimeError()
    except Exception:
      self.logger.critical('/deleteWebhook failed!')
    finally:
      self.terminate.set()
