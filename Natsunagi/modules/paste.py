import codecs
import os
import re
from io import BytesIO

import aiofiles
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from Natsunagi import eor
from Natsunagi import pgram as app
from Natsunagi.modules.helper_funcs.alternate import typing_action
from Natsunagi.modules.helper_funcs.decorators import natsunagicmd
from Natsunagi.modules.helper_funcs.misc import upload_text
from Natsunagi.utils.errors import capture_err
from Natsunagi.utils.keyboard import ikb
from Natsunagi.utils.pastebin import hpaste

__mod_name__ = "Paste"

pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")


@app.on_message(filters.command("bpaste") & ~filters.edited)
@capture_err
async def paste_funcs(_, message: Message):
    if not message.reply_to_message:
        return await eor(message, text="Reply To A Message With /paste")
    r = message.reply_to_message

    if not r.text and not r.document:
        return await eor(message, text="Only text and documents are supported.")

    m = await eor(message, text="Pasting...")

    if r.text:
        content = str(r.text)
    elif r.document:
        if r.document.file_size > 40000:
            return await m.edit("You can only paste files smaller than 40KB.")

        if not pattern.search(r.document.mime_type):
            return await m.edit("Only text files can be pasted.")

        doc = await message.reply_to_message.download()

        async with aiofiles.open(doc, mode="r") as f:
            content = await f.read()

        os.remove(doc)

    link = await hpaste(content)
    kb = ikb({"Paste Link": link})
    try:
        if m.from_user.is_bot:
            await message.reply_photo(
                photo=link,
                quote=False,
                reply_markup=kb,
            )
        else:
            await message.reply_photo(
                photo=link,
                quote=False,
                caption=f"**Paste Link:** [Here]({link})",
            )
        await m.delete()
    except Exception:
        await m.edit("Here's your paste", reply_markup=kb)


@natsunagicmd(command="hpaste")
def paste(update, context):
    msg = update.effective_message

    if msg.reply_to_message and msg.reply_to_message.document:
        file = context.bot.get_file(msg.reply_to_message.document)
        file.download("file.txt")
        text = codecs.open("file.txt", "r+", encoding="utf-8")
        paste_text = text.read()
        url = "https://www.toptal.com/developers/hastebin/documents"
        key = requests.post(url, data=paste_text.encode("UTF-8")).json().get("key")
        text = "**Pasted to Hastebin!!!**"
        buttons = [
            [
                InlineKeyboardButton(
                    text="View Link",
                    url=f"https://www.toptal.com/developers/hastebin/{key}",
                ),
                InlineKeyboardButton(
                    text="View Raw",
                    url=f"https://www.toptal.com/developers/hastebin/raw/{key}",
                ),
            ]
        ]
        msg.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        os.remove("file.txt")
    else:
        msg.reply_text("Give me a text file to paste on hastebin")
        return


@natsunagicmd(command="npaste")
@typing_action
def nekopaste(update, context):
    msg = update.effective_message

    if msg.reply_to_message and msg.reply_to_message.document:
        file = context.bot.get_file(msg.reply_to_message.document)
        file.download("file.txt")
        text = codecs.open("file.txt", "r+", encoding="utf-8")
        paste_text = text.read()
        link = (
            requests.post(
                "https://nekobin.com/api/documents",
                json={"content": paste_text},
            )
            .json()
            .get("result")
            .get("key")
        )
        text = "**Nekofied to Nekobin!!!**"
        buttons = [
            [
                InlineKeyboardButton(
                    text="View Link", url=f"https://nekobin.com/{link}"
                ),
                InlineKeyboardButton(
                    text="View Raw",
                    url=f"https://nekobin.com/raw/{link}",
                ),
            ]
        ]
        msg.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        os.remove("file.txt")
    else:
        msg.reply_text("Give me a text file to paste on nekobin")
        return


@natsunagicmd(command="spaste")
@typing_action
def spacepaste(update, context):
    message = update.effective_message
    bot, args = context.bot, context.args

    if not message.reply_to_message.text:
        file = bot.getFile(message.reply_to_message.document)
        file.download("file.txt")
        text = codecs.open("file.txt", "r+", encoding="utf-8")
        paste_text = text.read()
        print(paste_text)
        os.remove("file.txt")

    elif message.reply_to_message.text:
        paste_text = message.reply_to_message.text
    elif len(args) >= 1:
        paste_text = message.text.split(None, 1)[1]

    else:
        message.reply_text(
            "reply to any message or just do /paste <what you want to paste>"
        )
        return

    extension = "txt"
    url = "https://spaceb.in/api/v1/documents/"
    try:
        response = requests.post(
            url, data={"content": paste_text, "extension": extension}
        )
    except Exception as e:
        return {"error": str(e)}

    response = response.json()
    text = (
        f"**Pasted to [Space.bin]('https://spaceb.in/{response['payload']['id']}')!!!**"
    )
    buttons = [
        [
            InlineKeyboardButton(
                text="View Link", url=f"https://spaceb.in/{response['payload']['id']}"
            ),
            InlineKeyboardButton(
                text="View Raw",
                url=f"https://spaceb.in/api/v1/documents/{response['payload']['id']}/raw",
            ),
        ]
    ]
    message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


@natsunagicmd(command="pvpaste", pass_args=True)
def paste(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message

    if message.reply_to_message:
        data = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.document:
            file_info = context.bot.get_file(message.reply_to_message.document.file_id)
            with BytesIO() as file:
                file_info.download(out=file)
                file.seek(0)
                data = file.read().decode()

    elif len(args) >= 1:
        data = message.text.split(None, 1)[1]
    else:
        message.reply_text("What am I supposed to do with this?")
        return

    txt = ""
    paste_url = upload_text(data)
    if not paste_url:
        txt = "Failed to paste data"
    else:
        txt = "Successfully uploaded to [PrivateBin]({})".format(paste_url)

    message.reply_text(txt, disable_web_page_preview=True)


__mod_name__ = "Paste"

__help__ = """
❂ `/spaste`*:* Paste to spacebin
❂ `/npaste`*:* Paste to nekobin
❂ `/paste`*:* Paste to ezup
❂ `/bpaste`*:* Paste to batbin
❂ `/kpaste`*:* Paste to katbin
❂ `/ppaste`*:* Paste to pastylus
❂ `/cpaste`*:* Paste to catbin
❂ `/dpaste`*:* Paste to dogbin
❂ `/pvpaste`*:* Paste to privatebin
"""
