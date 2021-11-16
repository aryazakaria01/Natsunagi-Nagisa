import datetime
import requests
import os
import re
import urllib
import urllib.request

from datetime import datetime
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from random import randint
from typing import List
from telegram import ParseMode, InputMediaPhoto, Update, TelegramError, ChatAction
from telegram.ext import CommandHandler, run_async, CallbackContext

from Natsunagi import dispatcher
from Natsunagi.modules.disable import DisableAbleCommandHandler


def covid(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text.split(' ', 1)
    try:
       if len(text) == 1:
           r = requests.get("https://disease.sh/v3/covid-19/all").json()
           reply_text = f"**Global Totals** 🦠\nCases: {r['cases']:,}\nCases Today: {r['todayCases']:,}\nDeaths: {r['deaths']:,}\nDeaths Today: {r['todayDeaths']:,}\nRecovered: {r['recovered']:,}\nActive: {r['active']:,}\nCritical: {r['critical']:,}\nCases/Mil: {r['casesPerOneMillion']}\nDeaths/Mil: {r['deathsPerOneMillion']}"
       else:
           variabla = text[1]
           r = requests.get(
               f"https://disease.sh/v3/covid-19/countries/{variabla}").json()
           reply_text = f"**Cases for {r['country']} 🦠**\nCases: {r['cases']:,}\nCases Today: {r['todayCases']:,}\nDeaths: {r['deaths']:,}\nDeaths Today: {r['todayDeaths']:,}\nRecovered: {r['recovered']:,}\nActive: {r['active']:,}\nCritical: {r['critical']:,}\nCases/Mil: {r['casesPerOneMillion']}\nDeaths/Mil: {r['deathsPerOneMillion']}"
       message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        return msg.reply_text("There was a problem while importing the data!")


COVID_HANDLER = DisableAbleCommandHandler(["covid", "corona"], covid, run_async = True)
dispatcher.add_handler(COVID_HANDLER)
