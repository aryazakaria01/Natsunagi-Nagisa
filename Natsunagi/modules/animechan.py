import requests
from Natsunagi import pgram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Natsunagi.modules.helpers_funcs.chat_status import callbacks_in_filters


@pgram.on_callback_query(callbacks_in_filters('quotek'))
def callback_quotek(_, query):
    if query.data.split(":")[1] == "change":
        #         query.message.delete()
        kk = requests.get('https://animechan.vercel.app/api/random').json()
        anime = kk['anime']
        quote = kk['quote']
        character = kk['character']
        caption = f"""
**Anime:** `{anime}`
**Character:** `{character}`
**Quote:** `{quote}`"""
        query.message.edit(caption,
                           reply_markup=InlineKeyboardMarkup([
                               [
                                   InlineKeyboardButton(
                                       "Change", callback_data="quotek:change")
                               ],
                           ]))


@pgram.on_message(filters.command('quote'))
def quote(_, message):
    kk = requests.get('https://animechan.vercel.app/api/random').json()
    anime = kk['anime']
    quote = kk['quote']
    character = kk['character']
    caption = f"""
**Anime:** `{anime}`
**Character:** `{character}`
**Quote:** `{quote}`"""
    bot.send_message(message.chat.id,
                     caption,
                     reply_markup=InlineKeyboardMarkup([[
                         InlineKeyboardButton("Change",
                                              callback_data="quotek:change")
                     ]]))
