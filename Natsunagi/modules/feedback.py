import random

from telethon import Button

from Natsunagi import SUPPORT_CHAT
from Natsunagi import telethn as tbot
from Natsunagi.events import register


@register(pattern="/feedback")
async def feedback(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    Natsunagi = (
        "https://telegra.ph/file/753bfe51f0e0314f1f3ff.jpg",
        "https://telegra.ph/file/20bab4a499d6dccd823f1.jpg",
        "https://telegra.ph/file/2ef1c255ac51d9febb3f4.jpg",
        "https://telegra.ph/file/bc3a10df7c66e6333bba6.jpg",
        "https://telegra.ph/file/bf283996f928a6ab5b625.jpg",
        "https://telegra.ph/file/bf283996f928a6ab5b625.jpg",
        "https://telegra.ph/file/43b4f5a5645ab1cd1dd7c.jpg",
        "https://telegra.ph/file/0f5240ad4d50d5dac57fe.jpg",
        "https://telegra.ph/file/f6128a7a197cf088ba5e0.jpg",
        "https://telegra.ph/file/53d0320dcaa0d21da19c0.jpg",
        "https://telegra.ph/file/fc988e9441acfb5fe71a7.jpg",
        "https://telegra.ph/file/731387573fd96e3cfc2f5.jpg",
        "https://telegra.ph/file/41a2c085e2f6b60358779.jpg",
    )
    BUTTON = [[Button.url("Go To Support Group", f"https://t.me/{SUPPORT_CHAT}")]]
    TEXT = "Thanks For Your Feedback, I Hope You Happy With Our Service"
    logger_text = f"""
New Feedback Assigment

From User: {mention}
Username: @{e.sender.username}
User ID: {e.sender.id}
Feedback: {e.text}
"""
    await tbot.send_message(
        SUPPORT_CHAT,
        f"{logger_text}",
        file=random.choice(Natsunagi),
        link_preview=False,
    )
    await e.reply(TEXT, file=random.choice(Natsunagi), buttons=BUTTON)
