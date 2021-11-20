import requests

from telethon import events
from Natsunagi import telethn as Natsunagi

@Natsunagi.on(events.NewMessage(pattern="^/sylv ?(.*)"))
async def h(e):
 with requests.get("https://sylviorus.up.railway.app/user/{}".format(e.pattern_match.group(1))) as r:
  await e.reply(str(r.json()))
