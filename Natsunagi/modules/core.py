from Natsunagi import telethn as tbot
from Natsunagi.events import register
import os
import asyncio
import time
from datetime import datetime
from Natsunagi import OWNER_ID, DEV_USERS
from Natsunagi import TEMP_DOWNLOAD_DIRECTORY as path

water = "./Natsunagi/image/natsunagi.jpg"
client = tbot


@register(pattern=r"^/send ?(.*)")
async def Prof(event):
    if event.sender_id == OWNER_ID or event.sender_id == DEV_USERS:
        pass
    else:
        return
    thumb = water
    message_id = event.message.id
    input_str = event.pattern_match.group(1)
    the_plugin_file = "./Natsunagi/modules/{}.py".format(input_str)
    if os.path.exists(the_plugin_file):
        message_id = event.message.id
        await event.client.send_file(
            event.chat_id,
            the_plugin_file,
            force_document=True,
            allow_cache=False,
            thumb=thumb,
            reply_to=message_id,
        )
    else:
        await event.reply("No File Found!")
