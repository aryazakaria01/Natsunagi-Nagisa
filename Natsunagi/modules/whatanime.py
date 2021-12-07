import os
import time
import html
import aiohttp
import asyncio
import datetime
import tempfile
import bs4
import jikanpy
import requests

from jikanpy import Jikan
from jikanpy.exceptions import APIException
from pySmartDL import SmartDL
from telegraph import exceptions, upload_file
from urllib.parse import quote as urlencode
from decimal import Decimal
from datetime import timedelta, datetime
from urllib.parse import quote_plus
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Natsunagi import pgram

session = aiohttp.ClientSession()
progress_callback_data = {}
jikan = Jikan()

def format_bytes(size):
    size = int(size)
    # 2**10 = 1024
    power = 1024
    n = 0
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]+'B'}"


def return_progress_string(current, total):
    filled_length = int(30 * current // total)
    return "[" + "=" * filled_length + " " * (30 - filled_length) + "]"


def calculate_eta(current, total, start_time):
    if not current:
        return "00:00:00"
    end_time = time.time()
    elapsed_time = end_time - start_time
    seconds = (elapsed_time * (total / current)) - elapsed_time
    thing = "".join(str(timedelta(seconds=seconds)).split(".")[:-1]).split(", ")
    thing[-1] = thing[-1].rjust(8, "0")
    return ", ".join(thing)


@pgram.on_message(filters.command("whatanime", prefixes=(["!", "/"])))
async def whatanime(event):
    "Reverse search of anime."
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(
            event, "__reply to media to reverse search that anime__."
        )
    mediatype = media_type(reply)
    if mediatype not in ["Photo", "Video", "Gif", "Sticker"]:
        return await edit_delete(
            event,
            f"__Reply to proper media that is expecting photo/video/gif/sticker. not {mediatype}__.",
        )
    output = await _cattools.media_to_pic(event, reply)
    if output[1] is None:
        return await edit_delete(
            output[0], "__Unable to extract image from the replied message.__"
        )
    file = memory_file("anime.jpg", output[1])
    try:
        response = upload_file(file)
    except exceptions.TelegraphException as exc:
        try:
            response = upload_file(output[1])
        except exceptions.TelegraphException as exc:
            return await edit_delete(output[0], f"**Error :**\n__{exc}__")
    cat = f"https://telegra.ph{response[0]}"
    await output[0].edit("`Searching for result..`")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.trace.moe/search?anilistInfo&url={quote_plus(cat)}"
        ) as raw_resp0:
            resp0 = await raw_resp0.json()
        framecount = resp0["frameCount"]
        error = resp0["error"]
        if error != "":
            return await edit_delete(output[0], f"**Error:**\n__{error}__")
        js0 = resp0["result"]
        if not js0:
            return await output[0].edit("`No results found.`")
        js0 = js0[0]
        text = (
            f'**Titile Romaji : **`{html.escape(js0["anilist"]["title"]["romaji"])}`\n'
        )
        text += (
            f'**Titile Native :** `{html.escape(js0["anilist"]["title"]["native"])}`\n'
        )
        text += (
            f'**Titile English :** `{html.escape(js0["anilist"]["title"]["english"])}`\n'
            if js0["anilist"]["title"]["english"] is not None
            else ""
        )
        text += f'**Is Adult :** __{js0["anilist"]["isAdult"]}__\n'
        #         text += f'**File name :** __{js0["filename"]}__\n'
        text += f'**Episode :** __{html.escape(str(js0["episode"]))}__\n'
        text += f'**From :** __{readable_time(js0["from"])}__\n'
        text += f'**To :** __{readable_time(js0["to"])}__\n'
        percent = round(js0["similarity"] * 100, 2)
        text += f"**Similarity :** __{percent}%__\n"
        result = (
            f"**Searched {framecount} frames and found this as best result :**\n\n"
            + text
        )
        msg = await output[0].edit(result)
        try:
            await msg.reply(
                f'{readable_time(js0["from"])} - {readable_time(js0["to"])}',
                file=js0["video"],
            )
        except Exception:
            await msg.reply(
                f'{readable_time(js0["from"])} - {readable_time(js0["to"])}',
                file=js0["image"],
            )


async def progress_callback(current, total, reply):
    message_identifier = (reply.chat.id, reply.message_id)
    last_edit_time, prevtext, start_time = progress_callback_data.get(
        message_identifier, (0, None, time.time())
    )
    if current == total:
        try:
            progress_callback_data.pop(message_identifier)
        except KeyError:
            pass
    elif (time.time() - last_edit_time) > 1:
        if last_edit_time:
            download_speed = format_bytes(
                (total - current) / (time.time() - start_time)
            )
        else:
            download_speed = "0 B"
        text = f"""Downloading...
<code>{return_progress_string(current, total)}</code>
<b>Total Size:</b> {format_bytes(total)}
<b>Downladed Size:</b> {format_bytes(current)}
<b>Download Speed:</b> {download_speed}/s
<b>ETA:</b> {calculate_eta(current, total, start_time)}"""
        if prevtext != text:
            await reply.edit_text(text)
            prevtext = text
            last_edit_time = time.time()
            progress_callback_data[message_identifier] = (
                last_edit_time,
                prevtext,
                start_time,
            )
