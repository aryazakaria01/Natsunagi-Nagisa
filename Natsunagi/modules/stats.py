import os
import time
import psutil

from telegram import ParseMode, __version__ as peler
from platform import python_version as memek
from telethon import __version__ as tlh
from pyrogram import __version__ as pyr

import Natsunagi.modules.no_sql.users_db as user_db
from Natsunagi import StartTime
from Natsunagi.modules.helper_funcs import formatter

# Stats Module


async def bot_sys_stats():
    bot_uptime = int(time.time() - StartTime)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    process = psutil.Process(os.getpid())
    stats = f"""
arya@MacBook:~$ NatsunagiProBot:
------------------
Uptime: {formatter.get_readable_time((bot_uptime))}
CPU Usage: {cpu}%
Ram Usage: {mem}%
Disk: {disk}%
Python version: {memek()}
Library version: v{peler}
Telethon version: {tlh}
Pyrogram version: {pyr}
Users: {user_db.num_users()} users.
Groups: {user_db.num_chats()} groups.
"""

    return stats
