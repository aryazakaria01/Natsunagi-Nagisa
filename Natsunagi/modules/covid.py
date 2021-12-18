# Originally by gh @zYxDevs or tg @Yoga_CIC
# Don't remove, Respect me lol

import requests
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from Natsunagi import dispatcher
from Natsunagi.modules.disable import DisableAbleCommandHandler


def covid(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text.split(" ", 1)
    if len(text) == 1:
        try:
            r = requests.get("https://disease.sh/v3/covid-19/all").json()
            reply_text = f"*Global Totals* 🦠\nCases: `{r['cases']:,}`\nCases Today: `{r['todayCases']:,}`\nDeaths: `{r['deaths']:,}`\nDeaths Today: `{r['todayDeaths']:,}`\nRecovered: `{r['recovered']:,}`\nActive: `{r['active']:,}`\nCritical: `{r['critical']:,}`\nCases/Mil: `{r['casesPerOneMillion']}`\nDeaths/Mil: `{r['deathsPerOneMillion']}`"
            message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)
        except KeyError:
            message.reply_text("Not Found!")
            return
    if len(text) != 1:
        try:
            var = text[1]
            r = requests.get(f"https://disease.sh/v3/covid-19/countries/{var}").json()
            reply_text = f"*Cases for {r['country']}* 🦠\nCases: `{r['cases']:,}`\nCases Today: `{r['todayCases']:,}`\nDeaths: `{r['deaths']:,}`\nDeaths Today: `{r['todayDeaths']:,}`\nRecovered: `{r['recovered']:,}`\nActive: `{r['active']:,}`\nCritical: `{r['critical']:,}`\nCases/Mil: `{r['casesPerOneMillion']}`\nDeaths/Mil: `{r['deathsPerOneMillion']}`"
            message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)
        except KeyError:
            message.reply_text("Not Found!")
            return


COVID_HANDLER = DisableAbleCommandHandler(["covid", "corona"], covid, run_async=True)
dispatcher.add_handler(COVID_HANDLER)
