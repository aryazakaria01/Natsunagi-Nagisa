import requests

from Natsunagi import app
from Natsunagi.modules.helper_funcs.chat_status import call_back_in_filter
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@app.on_callback_query(call_back_in_filter("quotek"))
def callback_quotek(_, query):
    if query.data.split(":")[1] == "change":
        #         query.message.delete()
        kk = requests.get("https://animechan.vercel.app/api/random").json()
        anime = kk["anime"]
        quote = kk["quote"]
        character = kk["character"]
        caption = f"""
**Anime:** `{anime}`
**Character:** `{character}`
**Quote:** `{quote}`"""
        query.message.edit(
            caption,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Change Quote", callback_data="quotek:change"
                        )
                    ],
                ]
            ),
        )


@app.on_message(filters.command("animequote"))
def quote(_, message):
    kk = requests.get("https://animechan.vercel.app/api/random").json()
    anime = kk["anime"]
    quote = kk["quote"]
    character = kk["character"]
    caption = f"""
**Anime:** `{anime}`
**Character:** `{character}`
**Quote:** `{quote}`"""
    bot.send_message(
        message.chat.id,
        caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Change Quote", callback_data="quotek:change")]]
        ),
    )
