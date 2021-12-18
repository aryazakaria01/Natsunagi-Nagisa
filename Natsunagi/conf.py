import os
import sys

import yaml
from envparse import env

from Natsunagi import LOGGER

DEFAULTS = {
    "LOAD_MODULES": True,
    "DEBUG_MODE": True,
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_DB_FSM": 1,
    "MONGODB_URI": "localhost",
    "MONGO_DB": "Natsunagi",
    "API_PORT": 8080,
    "JOIN_CONFIRM_DURATION": "10m",
}

CONFIG_PATH = "data/bot_conf.yaml"
if os.name == "nt":
    LOGGER.debug("Detected Windows, changing config path...")
    CONFIG_PATH = os.getcwd() + "\\data\\bot_conf.yaml"

if os.path.isfile(CONFIG_PATH):
    LOGGER.info(CONFIG_PATH)
    for item in (
        data := yaml.safe_load(open("data/bot_conf.yaml", "r"), Loader=yaml.CLoader)
    ):
        DEFAULTS[item.upper()] = data[item]
else:
    LOGGER.info("Using env vars")


def get_list_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.list(name, default=default)) and not required:
        LOGGER.warn("No list key: " + name)
        return []
    if not data:
        LOGGER.critical("No list key: " + name)
        sys.exit(2)
    else:
        return data


def get_bool_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.bool(name, default=default)) and not required:
        LOGGER.warn("No bool key: " + name)
        return False
    if not data:
        LOGGER.critical("No bool key: " + name)
        sys.exit(2)
    else:
        return data


def get_str_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.str(name, default=default)) and not required:
        LOGGER.warn("No str key: " + name)
        return None
    if not data:
        LOGGER.critical("No str key: " + name)
        sys.exit(2)
    else:
        return data


def get_int_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.int(name, default=default)) and not required:
        LOGGER.warn("No int key: " + name)
        return None
    if not data:
        LOGGER.critical("No int key: " + name)
        sys.exit(2)
    else:
        return data
