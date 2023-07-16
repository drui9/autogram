import os
import sys
import json
from loguru import logger
from typing import Callable, Dict

default_config = {
  'lport': 4004,
  'media-quality': 'low',
  'telegram-token': None
}

def load_config(config_file : str, config_path : str):
  """Load configuration file from config_path dir"""
  if not os.path.exists(config_path):
    os.mkdir(config_path)
  #
  configuration = os.path.join(config_path, config_file)
  if not os.path.exists(configuration):
    with open(configuration, 'w') as conf:
      json.dump(default_config, conf, indent=3)
    logger.critical(f"Please edit [{configuration}]")
    sys.exit(0)
  config = {'config-file': configuration}
  with open(configuration, 'r') as conf:
    config |= json.load(conf)
  return config

def save_config(config :Dict):
  """config-file must be in the dictionary"""
  try:
    conffile = config.pop('config-file')
    with open(conffile, 'w') as conf:
      json.dump(config, conf, indent=2)
      conf.flush()
  except Exception:
    conffile = conffile or None
    if conffile:
      return config | {'config-file': conffile}
    else:
      logger.critical('Failed saving config file!')

def Start(config_file :str|None =None, config_path :str|None =None):
  """Call custom function with config as parameter"""
  config_path = config_path or os.getcwd()
  config_file = config_file or 'autogram.json'
  #
  def wrapper(func: Callable):
    return func(load_config(config_file, config_path))
  return wrapper
#

__all__ = [ "Start", "save_config", "load_config"]
