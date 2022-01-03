import os
import time

import psutil

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
Bot: {round(process.memory_info()[0] / 1024 ** 2)} MB
CPU: {cpu}%
Ram: {mem}%
Disk: {disk}%
Users: {user_db.num_users()} users.
Groups: {user_dn.num_chats()} groups.
"""

    return stats
