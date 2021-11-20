import asyncio
import logging
import os
import sys
import time
import spamwatch
import aiohttp
import telegram.ext as tg

from pyrogram import Client, errors
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid
from pyrogram.types import Message
from telethon import TelegramClient
from telethon.sessions import MemorySession
from telethon.sessions import StringSession
from motor import motor_asyncio
from odmantic import AIOEngine
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from redis import StrictRedis
from Python_ARQ import ARQ
from aiohttp import ClientSession
from telegram import Chat
from telegraph import Telegraph

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
logging.getLogger("pyrogram").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)
LOGGER.info(
    "Natsunagi is starting. | An CyberNetwork Project Parts. | Licensed under GPLv3."
)
LOGGER.info(
    "Not affiliated to Tantei Wa Mou or Villain in any way whatsoever."
)
LOGGER.info(
    "Project maintained by: github.com/aryazakaria01 (t.me/Badboyanim)"
)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting.",
    )
    sys.exit(1)

ENV = bool(os.environ.get("ENV", False))

if ENV:
    TOKEN = os.environ.get("TOKEN", None)

    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", None))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")

    JOIN_LOGGER = os.environ.get("JOIN_LOGGER", None)
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", None)

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
    EVENT_LOGS = os.environ.get("EVENT_LOGS", None) 
    ERROR_LOGS = os.environ.get("ERROR_LOGS", None) 
    WEBHOOK = bool(os.environ.get("WEBHOOK", False))
    URL = os.environ.get("URL", "")  
    PORT = int(os.environ.get("PORT", 8443)) 
    CERT_PATH = os.environ.get("CERT_PATH")
    API_ID = os.environ.get("API_ID", None) 
    API_HASH = os.environ.get("API_HASH", None) 
    DB_URL = os.environ.get("DATABASE_URL")
    DB_URL = DB_URL.replace(
        "postgres://", "postgresql://", 1
    )  
    DONATION_LINK = os.environ.get("DONATION_LINK") 
    LOAD = os.environ.get("LOAD", "").split() 
    NO_LOAD = os.environ.get("NO_LOAD", "translation").split() 
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", False)) 
    STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", False)) 
    WORKERS = int(os.environ.get("WORKERS", 8)) 
    BAN_STICKER = os.environ.get("BAN_STICKER", "CAADAgADOwADPPEcAXkko5EB3YGYAg") 
    ALLOW_EXCL = os.environ.get("ALLOW_EXCL", False) 
    TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./") 
    CASH_API_KEY = os.environ.get("CASH_API_KEY", None) 
    TIME_API_KEY = os.environ.get("TIME_API_KEY", None) 
    WALL_API = os.environ.get("WALL_API", None) 
    REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY", None) 
    OPENWEATHERMAP_ID = os.environ.get("OPENWEATHERMAP_ID", "") 
    GENIUS_API_TOKEN = os.environ.get("GENIUS_API_TOKEN", None) 
    MONGO_DB_URL = os.environ.get("MONGO_DB_URL", None) 
    REDIS_URL = os.environ.get("REDIS_URL", None) 
    BOT_ID = int(os.environ.get("BOT_ID", None)) 
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", None) 
    SPAMWATCH_SUPPORT_CHAT = os.environ.get("SPAMWATCH_SUPPORT_CHAT", None) 
    SPAMWATCH_API = os.environ.get("SPAMWATCH_API", None) 
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "") 
    STRING_SESSION = os.environ.get("STRING_SESSION", None) 
    APP_ID = os.environ.get("APP_ID", None) 
    APP_HASH = os.environ.get("APP_HASH", None) 
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", True) 
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", True) 
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", True)
    ALLOW_CHATS = os.environ.get("ALLOW_CHATS", True) 
    BOT_NAME = os.environ.get("BOT_NAME", True) 
    MONGO_DB = os.environ.get("MONGO_DB", "Natsunagi")
    ARQ_API_URL = os.environ.get("ARQ_API_URL", None)
    GOOGLE_CHROME_BIN = "/usr/bin/google-chrome"
    CHROME_DRIVER = "/usr/bin/chromedriver"
    BOT_API_URL = os.environ.get('BOT_API_URL', "https://api.telegram.org/bot")
    LOG_GROUP_ID = os.environ.get("LOG_GROUP_ID", None)
    HELP_IMG = os.environ.get("HELP_IMG", True)
    GROUP_START_IMG = os.environ.get("GROUP_START_IMG", True)
    NAGISA_PHOTO = os.environ.get("NAGISA_PHOTO", True)
    OPENWEATHERMAP_ID = os.environ.get("OPENWEATHERMAP_ID", "")
    ARQ_API_KEY = os.environ.get("ARQ_API_KEY", None)
    IBM_WATSON_CRED_URL = os.environ.get("IBM_WATSON_CRED_URL", None)
    IBM_WATSON_CRED_PASSWORD = os.environ.get("IBM_WATSON_CRED_PASSWORD", None)
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
    STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", False))
    WORKERS = int(os.environ.get("WORKERS", 8))
    REPOSITORY = os.environ.get("REPOSITORY", "")
    WHITELIST_CHATS = os.environ.get('WHITELIST_CHATS', "")
    MONGO_PORT = os.environ.get("MONGO_PORT", None)
    
    try:
        WHITELIST_CHATS = set(int(x) for x in os.environ.get('WHITELIST_CHATS', "").split())
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
    CASH_API_KEY = Config.CASH_API_KEY
    TIME_API_KEY = Config.TIME_API_KEY
    WALL_API = Config.WALL_API
    MONGO_DB_URL = Config.MONGO_DB_URL
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
    STRING_SESSION = Config.STRING_SESSION
    GENIUS_API_TOKEN = Config.GENIUS_API_TOKEN
    YOUTUBE_API_KEY = Config.YOUTUBE_API_KEY
    ALLOW_EXCL = Config.ALLOW_EXCL
    TEMP_DOWNLOAD_DIRECTORY = Config.TEMP_DOWNLOAD_DIRECTORY
    ARQ_API_URL = Config.ARQ_API_URL
    GOOGLE_CHROME_BIN = Config.GOOGLE_CHROME_BIN
    CHROME_DRIVER = Config.CHROME_DRIVER
    BOT_NAME = Config.BOT_NAME
    DEL_CMDS = Config.DEL_CMDS
    BOT_API_URL = Config.BOT_API_URL
    MONGO_DB_URL = Config.MONGO_DB_URL
    MONGO_DB = Config.MONGO_DB
    HELP_IMG = Config.HELP_IMG
    START_IMG = Config.START_IMG
    NAGISA_PHOTO = Config.NAGISA_PHOTO
    LOG_GROUP_ID = Config.LOG_GROUP_ID
    OPENWEATHERMAP_ID = Config.OPENWEATHERMAP_ID
    ARQ_API_KEY = Config.ARQ_API_KEY
    IBM_WATSON_CRED_URL = Config.IBM_WATSON_CRED_URL
    IBM_WATSON_CRED_PASSWORD = Config.IBM_WATSON_CRED_PASSWORD
    WORKERS = Config.WORKERS
    STRICT_GBAN = Config.STRICT_GBAN
    DEL_CMDS = Config.DEL_CMDS
    REPOSITORY = Config.REPOSITORY
    WHITELIST_CHATS = Config.WHITELIST_CHATS
    MONGO_PORT = Config.MONGO_PORT
    
    try:
        BL_CHATS = {int(x) for x in Config.BL_CHATS or []}
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")
        

DRAGONS.add(OWNER_ID)
DEV_USERS.add(OWNER_ID)
DEV_USERS.add(870471128)
DEV_USERS.add(645739169)
DEV_USERS.add(1416529201)
DEV_USERS.add(1192108540)

REDIS = StrictRedis.from_url(REDIS_URL, decode_responses=True)

try:

    REDIS.ping()

    LOGGER.info("Connecting To Redis Database")

except BaseException:

    raise Exception("[Natsunagi Error]: Your Redis Database Is Not Alive, Please Check Again.")

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
        LOGGER.warning("[Natsunagi Error]: Can't connect to SpamWatch!")

telegraph = Telegraph()
telegraph.create_account(short_name='Natsunagi')
updater = tg.Updater(token=TOKEN, base_url=BOT_API_URL, workers=WORKERS, request_kwargs={"read_timeout": 10, "connect_timeout": 10}, use_context=True)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
dispatcher = updater.dispatcher
session_name = TOKEN.split(":")[0]
pgram = Client(
    session_name,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
)
mongodb = MongoClient(MONGO_DB_URL, 27017)[MONGO_DB]
motor = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)
db = motor[MONGO_DB]
engine = AIOEngine(motor, MONGO_DB)
aiohttpsession = ClientSession()
# ARQ Client
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)
ubot = TelegramClient(StringSession(STRING_SESSION), APP_ID, APP_HASH)
pbot = Client("NatsunagiBot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)
app = Client("Natsunagi", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
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
    CustomCommandHandler,
    CustomMessageHandler,
    CustomRegexHandler,
)

tg.RegexHandler = CustomRegexHandler
tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
