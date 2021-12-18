import random

from telethon import Button
from Natsunagi import SUPPORT_CHAT, telethn as tbot
from Natsunagi.events import register

@register(pattern="/feedback")
async def feedback(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = "["+user_name+"](tg://user?id="+str(user_id)+")" 
    OWO = (
      "https://telegra.ph/file/5a03a79acba8d3c407056.jpg",
      "https://telegra.ph//file/15ab1c01c8ed09a7ffc95.jpg",
      "https://telegra.ph/file/b4af1ee5c4179e8833d6d.jpg",
      "https://telegra.ph/file/15f2fb8f2ff8c0bf2bd06.jpg",
      "https://telegra.ph//file/5a3ec69041389b4fbcc2a.jpg",
)
    BUTTON = [[Button.url("Click", f"https://t.me/{SUPPORT_CHAT}")]]
    TEXT = "Thanks For Your Feedback, I Hope You Happy With Our Service"
    logger_text = f"""
New Feedback Assigment

From User: {mention}
Username: @{e.sender.username}
User ID: {e.sender.id}
Feedback: {e.text}
"""
    await tbot.send_message(SUPPORT_CHAT, f"{logger_text}", file=random.choice(OWO), link_preview=False)
    await e.reply(TEXT, file=random.choice(OWO), buttons=BUTTON)
