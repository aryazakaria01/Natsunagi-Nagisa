import os
import time

import psutil

import Natsunagi.modules.sql.users_sql as sql
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
root@FurryChemistry:~$ Natsunagi:
------------------
├-☉️⇝  UPTIME: {formatter.get_readable_time((bot_uptime))}
├-☉️⇝  BOT: {round(process.memory_info()[0] / 1024 ** 2)} MB
├-☉️⇝  CPU: {cpu}%
├-☉️⇝ 🖲RAM: {mem}%
├-☉️⇝  DISK: {disk}%
├-☉️⇝  USERS: {sql.num_users()} users.
└-☉️⇝  GROUPS: {sql.num_chats()} groups.
"""

    return stats
