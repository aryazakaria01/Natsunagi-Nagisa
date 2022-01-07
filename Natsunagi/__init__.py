import asyncio
import logging
import os
import sys
import time
import json
from inspect import getfullargspec

import spamwatch
import telegram.ext as tg
from aiohttp import ClientSession
from ptbcontrib.postgres_persistence import PostgresPersistence
from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, PeerIdInvalid
from pyrogram.types import Message
from Python_ARQ import ARQ
from redis import StrictRedis
from telegram import Chat
from telegraph import Telegraph
from telethon import TelegramClient
from telethon.sessions import MemorySession

StartTime = time.time()


def get_user_list(__init__, key):
    with open("{}/Natsunagi/{}".format(os.getcwd(), __init__), "r") as json_file:
        return json.load(json_file)[key]


# enable logging
FORMAT = "[Natsunagi] %(message)s"
logging.basicConfig(
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
)
logging.getLogger("pyrogram").setLevel(logging.INFO)
logging.getLogger("ptbcontrib.postgres_persistence.postgrespersistence").setLevel(
    logging.WARNING
)

LOGGER = logging.getLogger("[Natsunagi]")
LOGGER.info(
    "Natsunagi is starting. | An CyberNetwork Project Parts. | Licensed under GPLv3."
)
LOGGER.info("Not affiliated to Tantei Wa Mou or Villain in any way whatsoever.")
LOGGER.info("Project maintained by: github.com/aryazakaria01 (t.me/FurryChemistry)")

# if version < 3.10, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 10:
    LOGGER.error(
        "You MUST have a python version of at least 3.10! Multiple features depend on this. Bot quitting.",
    )
    sys.exit(1)

ENV = bool(os.environ.get("ENV", False))

if ENV:
    TOKEN = os.environ.get("TOKEN")

    try:
        OWNER_ID = int(os.environ.get("OWNER_ID"))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")

    JOIN_LOGGER = os.environ.get("JOIN_LOGGER")
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME")

    try:
        DRAGONS = {int(x) for x in os.environ.get("DRAGONS", "").split()}
        DEV_USERS = {int(x) for x in os.environ.get("DEV_USERS", "").split()}
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    try:
        DEMONS = {int(x) for x in os.environ.get("DEMONS", "").split()}
    except ValueError:
        raise Exception("Your support users list does not contain valid integers.")

    try:
        WOLVES = {int(x) for x in os.environ.get("WOLVES", "").split()}
    except ValueError:
        raise Exception("Your whitelisted users list does not contain valid integers.")

    try:
        TIGERS = {int(x) for x in os.environ.get("TIGERS", "").split()}
    except ValueError:
        raise Exception("Your scout users list does not contain valid integers.")

    INFOPIC = bool(os.environ.get("INFOPIC", False))
    DEBUG = bool(os.environ.get("DEBUG", False))
    EVENT_LOGS = os.environ.get("EVENT_LOGS")
    ERROR_LOGS = os.environ.get("ERROR_LOGS")
    WEBHOOK = bool(os.environ.get("WEBHOOK", False))
    URL = os.environ.get("URL", "")
    PORT = int(os.environ.get("PORT", 8443))
    CERT_PATH = os.environ.get("CERT_PATH")
    API_ID = os.environ.get("API_ID")
    API_HASH = os.environ.get("API_HASH")
    DB_URL = os.environ.get("DATABASE_URL")
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
    DONATION_LINK = os.environ.get("DONATION_LINK")
    LOAD = os.environ.get("LOAD", "").split()
    NO_LOAD = os.environ.get("NO_LOAD", "translation").split()
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
    STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", False))
    WORKERS = int(os.environ.get("WORKERS", 8))
    BAN_STICKER = os.environ.get("BAN_STICKER", "CAADAgADOwADPPEcAXkko5EB3YGYAg")
    ALLOW_EXCL = os.environ.get("ALLOW_EXCL", False)
    TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./")
    TIME_API_KEY = os.environ.get("TIME_API_KEY")
    WALL_API = os.environ.get("WALL_API")
    REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY")
    OPENWEATHERMAP_ID = os.environ.get("OPENWEATHERMAP_ID", "")
    REDIS_URL = os.environ.get("REDIS_URL")
    BOT_ID = int(os.environ.get("BOT_ID"))
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT")
    SPAMWATCH_SUPPORT_CHAT = os.environ.get("SPAMWATCH_SUPPORT_CHAT")
    SPAMWATCH_API = os.environ.get("SPAMWATCH_API")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
    APP_ID = os.environ.get("APP_ID")
    APP_HASH = os.environ.get("APP_HASH")
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", True)
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", True)
    ALLOW_CHATS = os.environ.get("ALLOW_CHATS", True)
    BOT_NAME = os.environ.get("BOT_NAME", True)
    MONGO_DB = os.environ.get("MONGO_DB", "Natsunagi")
    MONGO_URI = os.environ.get("MONGO_URI")
    ARQ_API_URL = os.environ.get("ARQ_API_URL")
    BOT_API_URL = os.environ.get("BOT_API_URL", "https://api.telegram.org/bot")
    LOG_GROUP_ID = os.environ.get("LOG_GROUP_ID")
    OPENWEATHERMAP_ID = os.environ.get("OPENWEATHERMAP_ID", "")
    ARQ_API_KEY = os.environ.get("ARQ_API_KEY")
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
    MONGO_PORT = os.environ.get("MONGO_PORT")
    CUSTOM_CMD = os.environ.get("CUSTOM_CMD", "?")
    GENIUS_API_TOKEN = os.environ.get("GENIUS_API_TOKEN")
    CASH_API_KEY = os.environ.get("CASH_API_KEY", None)

    try:
        WHITELIST_CHATS = {
            int(x) for x in os.environ.get("WHITELIST_CHATS", "").split()
        }
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

    try:
        BL_CHATS = {int(x) for x in os.environ.get("BL_CHATS", "").split()}
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

else:
    from Natsunagi.config import Development as Config

    TOKEN = Config.TOKEN

    try:
        OWNER_ID = int(Config.OWNER_ID)
    except ValueError:
        raise Exception("Your OWNER_ID variable is not a valid integer.")

    JOIN_LOGGER = Config.JOIN_LOGGER
    OWNER_USERNAME = Config.OWNER_USERNAME
    ALLOW_CHATS = Config.ALLOW_CHATS
    try:
        DRAGONS = {int(x) for x in Config.DRAGONS or []}
        DEV_USERS = {int(x) for x in Config.DEV_USERS or []}
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    try:
        DEMONS = {int(x) for x in Config.DEMONS or []}
    except ValueError:
        raise Exception("Your support users list does not contain valid integers.")

    try:
        WOLVES = {int(x) for x in Config.WOLVES or []}
    except ValueError:
        raise Exception("Your whitelisted users list does not contain valid integers.")

    try:
        TIGERS = {int(x) for x in Config.TIGERS or []}
    except ValueError:
        raise Exception("Your tiger users list does not contain valid integers.")

    INFOPIC = Config.INFOPIC
    EVENT_LOGS = Config.EVENT_LOGS
    ERROR_LOGS = Config.ERROR_LOGS
    WEBHOOK = Config.WEBHOOK
    URL = Config.URL
    PORT = Config.PORT
    CERT_PATH = Config.CERT_PATH
    API_ID = Config.API_ID
    API_HASH = Config.API_HASH
    DB_URL = Config.SQLALCHEMY_DATABASE_URI
    DONATION_LINK = Config.DONATION_LINK
    STRICT_GBAN = Config.STRICT_GBAN
    WORKERS = Config.WORKERS
    BAN_STICKER = Config.BAN_STICKER
    TEMP_DOWNLOAD_DIRECTORY = Config.TEMP_DOWNLOAD_DIRECTORY
    LOAD = Config.LOAD
    NO_LOAD = Config.NO_LOAD
    WALL_API = Config.WALL_API
    REDIS_URL = Config.REDIS_URL
    SUPPORT_CHAT = Config.SUPPORT_CHAT
    SPAMWATCH_SUPPORT_CHAT = Config.SPAMWATCH_SUPPORT_CHAT
    SPAMWATCH_API = Config.SPAMWATCH_API
    REM_BG_API_KEY = Config.REM_BG_API_KEY
    OPENWEATHERMAP_ID = Config.OPENWEATHERMAP_ID
    APP_ID = Config.APP_ID
    APP_HASH = Config.APP_HASH
    BOT_ID = Config.BOT_ID
    BOT_USERNAME = Config.BOT_USERNAME
    ALLOW_EXCL = Config.ALLOW_EXCL
    ARQ_API_URL = Config.ARQ_API_URL
    BOT_NAME = Config.BOT_NAME
    DEL_CMDS = Config.DEL_CMDS
    BOT_API_URL = Config.BOT_API_URL
    MONGO_DB = Config.MONGO_DB
    MONGO_URI = Config.MONG_URI
    LOG_GROUP_ID = Config.LOG_GROUP_ID
    OPENWEATHERMAP_ID = Config.OPENWEATHERMAP_ID
    ARQ_API_KEY = Config.ARQ_API_KEY
    DEL_CMDS = Config.DEL_CMDS
    MONGO_PORT = Config.MONGO_PORT
    CUSTOM_CMD = Config.CUSTOM_CMD
    GENIUS_API_TOKEN = Config.GENIUS_API_TOKEN
    CASH_API_KEY = Config.CASH_API_KEY

    try:
        BL_CHATS = {int(x) for x in Config.BL_CHATS or []}
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")


DRAGONS.add(OWNER_ID)
DEV_USERS.add(OWNER_ID)


REDIS = StrictRedis.from_url(REDIS_URL, decode_responses=True)
try:
    REDIS.ping()
    LOGGER.info("Connecting To Redis Database")
except BaseException:
    raise Exception(
        "[Natsunagi Error]: Your Redis Database Is Not Alive, Please Check Again."
    )
finally:
    REDIS.ping()
    LOGGER.info("Connection To The Redis Database Established Successfully!")


if not SPAMWATCH_API:
    sw = None
    LOGGER.warning("SpamWatch API key Is Missing! Recheck Your Config.")
else:
    try:
        sw = spamwatch.Client(SPAMWATCH_API)
    except:
        sw = None
        LOGGER.warning("Can't connect to SpamWatch!")

from Natsunagi.modules.sql import SESSION

telegraph = Telegraph()
telegraph.create_account(short_name="Natsunagi")
defaults = tg.Defaults(run_async=True)
updater = tg.Updater(
    token=TOKEN,
    base_url=BOT_API_URL,
    workers=min(32, os.cpu_count() + 4),
    request_kwargs={"read_timeout": 10, "connect_timeout": 10},
    use_context=True,
    persistence=PostgresPersistence(session=SESSION),
)
# Telethon
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
# Dispacther
dispatcher = updater.dispatcher
session_name = TOKEN.split(":")[0]
pgram = Client(
    session_name,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
)
# AioHttp Session
aiohttpsession = ClientSession()
# ARQ Client
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)
loop = asyncio.get_event_loop()


async def get_entity(client, entity):
    entity_client = client
    if not isinstance(entity, Chat):
        try:
            entity = int(entity)
        except ValueError:
            pass
        except TypeError:
            entity = entity.id
        try:
            entity = await client.get_chat(entity)
        except (PeerIdInvalid, ChannelInvalid):
            for pgram in apps:
                if pgram != client:
                    try:
                        entity = await pgram.get_chat(entity)
                    except (PeerIdInvalid, ChannelInvalid):
                        pass
                    else:
                        entity_client = pgram
                        break
            else:
                entity = await pgram.get_chat(entity)
                entity_client = pgram
    return entity, entity_client


apps = [pgram]
DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)
WOLVES = list(WOLVES)
DEMONS = list(DEMONS)
TIGERS = list(TIGERS)

async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


from Natsunagi.modules.helper_funcs.handlers import (
    CustomMessageHandler,
    CustomRegexHandler,
)

tg.RegexHandler = CustomRegexHandler
tg.MessageHandler = CustomMessageHandler

from Natsunagi.modules.helper_funcs.handlers import CustomCommandHandler

if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    tg.CommandHandler = CustomCommandHandler
