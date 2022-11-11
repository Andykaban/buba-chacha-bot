import os
import logging

import yaml

logging.basicConfig(format='%(levelname)s | %(message)s', level='INFO')
logger = logging.getLogger()

BOT_CONFIG = {}


def load_config(config_file):
    global BOT_CONFIG

    if not os.path.isfile(config_file):
        logger.error(f'Bot config file {config_file} is not found!')
        raise OSError
    with open(config_file) as f_in:
        BOT_CONFIG.update(yaml.safe_load(f_in))

