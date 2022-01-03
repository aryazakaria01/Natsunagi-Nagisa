import datetime

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from requests import get

from Natsunagi import pgram as bot


def call_back_in_filter(data):
    return filters.create(lambda flt, _, query: flt.data in query.data, data=data)


def latest():

    url = "https://subsplease.org/api/?f=schedule&h=true&tz=Japan"
    res = get(url).json()

    k = None
    for x in res["schedule"]:
        title = x["title"]
        time = x["time"]
        try:
            aired = bool(x["aired"])
            title = (
                f"**[{title}](https://subsplease.org/shows/{x['page']})**"
                if not aired
                else f"**~~[{title}](https://subsplease.org/shows/{x['page']})~~**"
            )
        except KeyError:
            title = f"**[{title}](https://subsplease.org/shows/{x['page']})**"
        data = f"{title} - {time}"

        if k:
            k = f"{k}\n{data}"

        else:
            k = data

    return k


@bot.on_message(filters.command("latest"))
def lates(_, message):
    mm = latest()
    message.reply_text(
        f"Today's Schedule From Japan:\n\nTZ: Japan\n{mm}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refresh", callback_data="fk")]]
        ),
    )


@bot.on_callback_query(call_back_in_filter("fk"))
def callbackk(_, query):

    if query.data == "fk":
        mm = latest()
        time_ = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")

        try:
            query.message.edit(
                f"Today's Schedule From Japan:\n\nTZ: Japan\n{mm}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Refresh", callback_data="fk")]]
                ),
            )
            query.answer("Refreshed the schedule!")

        except:
            query.answer("Refreshed the schedule!")
