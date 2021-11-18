import html
import random
import time
import glob
import requests
import requests as r
import urllib.request
import os

import Natsunagi.modules.fun_strings as fun_strings

from pyrogram import filters
from pathlib import Path
from Natsunagi import DEMONS, DRAGONS, pgram as bot, dispatcher, BOT_USERNAME, BOT_NAME
from Natsunagi.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler
from Natsunagi.modules.helper_funcs.chat_status import is_user_admin
from Natsunagi.modules.helper_funcs.alternate import typing_action
from Natsunagi.modules.helper_funcs.extraction import extract_user
from telegram import ChatPermissions, ParseMode, Update, Bot
from telegram.error import BadRequest
from telegram.ext import CallbackContext, run_async, Filters
from telegram.utils.helpers import escape_markdown

GIF_ID = "CgACAgQAAx0CSVUvGgAC7KpfWxMrgGyQs-GUUJgt-TSO8cOIDgACaAgAAlZD0VHT3Zynpr5nGxsE"

#sleep how many times after each edit in 'love' 
EDIT_SLEEP = 1
#edit how many times in 'love' 
EDIT_TIMES = 10


#sleep how many times after each edit in 'bombs' 
EDIT_SLEEP = 1
#edit how many times in 'bombs' 
EDIT_TIMES = 9


#sleep how many times after each edit in 'hack' 
EDIT_SLEEP = 1
#edit how many times in 'hack' 
EDIT_TIMES = 10


#sleep how many times after each edit in 'earthanimation' 
EDIT_SLEEP = 1
#edit how many times in 'earthanimation' 
EDIT_TIMES = 18


#sleep how many times after each edit in 'moonanimation' 
EDIT_SLEEP = 1
#edit how many times in 'moonanimation' 
EDIT_TIMES = 32


#sleep how many times after each edit in 'clockanimation' 
EDIT_SLEEP = 1
#edit how many times in 'clockanimation' 
EDIT_TIMES = 11


#sleep how many times after each edit in 'blockanimation' 
EDIT_SLEEP = 1
#edit how many times in 'blockanimation' 
EDIT_TIMES = 18


#sleep how many times after each edit in 'kill' 
EDIT_SLEEP = 1
#edit how many times in 'kill' 
EDIT_TIMES = 12


block_chain = [
             "🟥",
             "🟧",
             "🟨",
             "🟩",
             "🟦",
             "🟪",
             "🟫",
             "⬛",
             "⬜",
             "🟥",
             "🟧",
             "🟨",
             "🟩",
             "🟦",
             "🟪",
             "🟫",
             "⬛",
             "⬜"
]

love_siren = [
            "❤️❤️❤️🧡🧡🧡💚💚💚\n💙💙💙💜💜💜🖤🖤🖤",
            "🖤🖤🖤💜💜💜💙💙💙\n❤️❤️❤️🧡🧡🧡💚💚💚",
            "💛💛💛💙💙💙❤️❤️❤️\n💜💜💜❤️❤️❤️🧡🧡🧡",
            "❤️❤️❤️🧡🧡🧡💚💚💚\n💙💙💙💜💜💜🖤🖤🖤",
            "🖤🖤🖤💜💜💜💙💙💙\n❤️❤️❤️🧡🧡🧡💚💚💚",
            "💛💛💛💙💙💙❤️❤️❤️\n💜💜💜❤️❤️❤️🧡🧡🧡",
            "❤️❤️❤️🧡🧡🧡💚💚💚\n💙💙💙💜💜💜🖤🖤🖤",
            "🖤🖤🖤💜💜💜💙💙💙\n❤️❤️❤️🧡🧡🧡💚💚💚",
            "💛💛💛💙💙💙❤️❤️❤️\n💜💜💜❤️❤️❤️🧡🧡🧡"
]


bomb_ettu = [
             "▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️",
             "💣💣💣💣\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️", 
             "▪️▪️▪️▪️\n💣💣💣💣\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️",
             "▪️▪️▪️▪️\n▪️▪️▪️▪️\n💣💣💣💣\n▪️▪️▪️▪️\n▪️▪️▪️▪️",
             "▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n💣💣💣💣\n▪️▪️▪️▪️",
             "▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n💣💣💣💣",
             "▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n💥💥💥💥",
             "▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n💥💥💥💥\n💥💥💥💥",
             "▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n▪️▪️▪️▪️\n😵😵😵😵",
]



def runs(update: Update, context: CallbackContext):
    temp = random.choice(fun_strings.RUN_STRINGS)
    if update.effective_user.id == 1170714920:
        temp = "Run everyone, they just dropped a bomb 💣💣"
    update.effective_message.reply_text(temp)


@typing_action
def goodnight(update, context):
    message = update.effective_message
    first_name = update.effective_user.first_name
    reply = f"Good Night! {escape_markdown(first_name)}" 
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


@typing_action
def goodmorning(update, context):
    message = update.effective_message
    first_name = update.effective_user.first_name
    reply = f"Good Morning! {escape_markdown(first_name)}"
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
	
	
def slap(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat

    reply_text = (
        message.reply_to_message.reply_text
        if message.reply_to_message
        else message.reply_text
    )

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id == bot.id:
        temp = random.choice(fun_strings.SLAP_CUTIEPII_TEMPLATES)

        if isinstance(temp, list):
            if temp[2] == "tmute":
                if is_user_admin(chat, message.from_user.id):
                    reply_text(temp[1])
                    return

                mutetime = int(time.time() + 60)
                bot.restrict_chat_member(
                    chat.id,
                    message.from_user.id,
                    until_date=mutetime,
                    permissions=ChatPermissions(can_send_messages=False),
                )
            reply_text(temp[0])
        else:
            reply_text(temp)
        return

    if user_id:

        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(slapped_user.first_name)

    else:
        user1 = bot.first_name
        user2 = curr_user

    temp = random.choice(fun_strings.SLAP_TEMPLATES)
    item = random.choice(fun_strings.ITEMS)
    hit = random.choice(fun_strings.HIT)
    throw = random.choice(fun_strings.THROW)

    if update.effective_user.id == 1096215023:
        temp = "@NeoTheKitty scratches {user2}"

    reply = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(reply, parse_mode=ParseMode.HTML)


def pat(update: Update, _):
    msg = update.effective_message
    pat = requests.get("https://some-random-api.ml/animu/pat").json()
    link = pat.get("link")
    if not link:
        msg.reply_text("No URL was received from the API!")
        return
    msg.reply_video(link)

	
def roll(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(range(1, 7)))


def toss(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(fun_strings.TOSS))


def shrug(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )
    reply_text(r"¯\_(ツ)_/¯")


def bluetext(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )
    reply_text(
        "/BLUE /TEXT\n/MUST /CLICK\n/I /AM /A /STUPID /ANIMAL /THAT /IS /ATTRACTED /TO /COLORS",
    )


def rlg(update: Update, context: CallbackContext):
    eyes = random.choice(fun_strings.EYES)
    mouth = random.choice(fun_strings.MOUTHS)
    ears = random.choice(fun_strings.EARS)

    if len(eyes) == 2:
        repl = ears[0] + eyes[0] + mouth[0] + eyes[1] + ears[1]
    else:
        repl = ears[0] + eyes[0] + mouth[0] + eyes[0] + ears[1]
    update.message.reply_text(repl)


def decide(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun_strings.DECIDE))


def table(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun_strings.TABLE))


normiefont = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]

weebyfont = [
    "卂",
    "乃",
    "匚",
    "刀",
    "乇",
    "下",
    "厶",
    "卄",
    "工",
    "丁",
    "长",
    "乚",
    "从",
    "𠘨",
    "口",
    "尸",
    "㔿",
    "尺",
    "丂",
    "丅",
    "凵",
    "リ",
    "山",
    "乂",
    "丫",
    "乙",
]

def weebify(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    string = ""

    if message.reply_to_message:
        string = message.reply_to_message.text.lower().replace(" ", "  ")

    if args:
        string = "  ".join(args).lower()

    if not string:
        message.reply_text("Usage is `/weebify <text>`", parse_mode=ParseMode.MARKDOWN)
        return

    for normiecharacter in string:
        if normiecharacter in normiefont:
            weebycharacter = weebyfont[normiefont.index(normiecharacter)]
            string = string.replace(normiecharacter, weebycharacter)

    if message.reply_to_message:
        message.reply_to_message.reply_text(string)
    else:
        message.reply_text(string)

def gbun(update, context):
    user = update.effective_user
    chat = update.effective_chat

    if update.effective_message.chat.type == "private":
        return
    if int(user.id) in DRAGONS or int(user.id) in DEMONS:
        context.bot.sendMessage(chat.id, (random.choice(fun_strings.GBUN)))


def gbam(update, context):
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    message = update.effective_message

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id:
        gbam_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(gbam_user.first_name)

    else:
        user1 = curr_user
        user2 = bot.first_name

    if update.effective_message.chat.type == "private":
        return
    if int(user.id) in DRAGONS or int(user.id) in DEMONS:
        gbamm = fun_strings.GBAM
        reason = random.choice(fun_strings.GBAM_REASON)
        gbam = gbamm.format(user1=user1, user2=user2, chatid=chat.id, reason=reason)
        context.bot.sendMessage(chat.id, gbam, parse_mode=ParseMode.HTML)

def cuddle(update: Update, context: CallbackContext):
	bot = context.bot
	args = context.args
	message = update.effective_message

	reply_to = message.reply_to_message or message

	curr_user = html.escape(message.from_user.first_name)
	user_id = extract_user(message, args)

	if user_id:
	    cuddled_user = bot.get_chat(user_id)
	    user1 = curr_user
	    user2 = html.escape(cuddled_user.first_name)

	else:
	    user1 = bot.first_name
	    user2 = curr_user

	cuddle_type = random.choice(("Text", "Gif"))
	if cuddle_type == "Gif":
	    try:
	        temp = random.choice(fun_strings.CUDDLE_GIF)
	        reply_to.reply_animation(temp)
	    except BadRequest:
	        cuddle_type = "Text"

	if cuddle_type == "Text":
	    temp = random.choice(fun_strings.CUDDLE_TEMPLATES)
	    reply = temp.format(user1=user1, user2=user2)
	    reply_to.reply_text(reply, parse_mode=ParseMode.HTML)


def flirt(update: Update, context: CallbackContext):
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(fun_strings.FLIRT_TEXT))

	
def romance(update: Update, context: CallbackContext):
	bot = context.bot
	args = context.args
	message = update.effective_message

	reply_to = message.reply_to_message or message

	curr_user = html.escape(message.from_user.first_name)
	user_id = extract_user(message, args)

	if user_id:
	    romantic_user = bot.get_chat(user_id)
	    user1 = curr_user
	    user2 = html.escape(romantic_user.first_name)

	else:
	    user1 = bot.first_name
	    user2 = curr_user

	romance_type = random.choice(("Text", "Gif", "Sticker"))
	if romance_type == "Gif":
	    try:
	        temp = random.choice(fun_strings.ROMANCE_GIFS)
	        reply_to.reply_animation(temp)
	    except BadRequest:
	        romance_type = "Text"

	if romance_type == "Sticker":
	    try:
	        temp = random.choice(fun_strings.ROMANCE_STICKERS)
	        reply_to.reply_sticker(temp)
	    except BadRequest:
	        romance_type = "Text"

	if romance_type == "Text":
	    temp = random.choice(fun_strings.ROMANCE_TEMPLATES)
	    reply = temp.format(user1=user1, user2=user2)
	    reply_to.reply_text(reply, parse_mode=ParseMode.HTML)


def owo(update: Update, context: CallbackContext):
	bot = context.bot
	args = context.args
	message = update.effective_message

	reply_to = message.reply_to_message or message

	curr_user = html.escape(message.from_user.first_name)
	user_id = extract_user(message, args)

	if user_id:
	    owo_user = bot.get_chat(user_id)
	    user1 = curr_user
	    user2 = html.escape(owo_user.first_name)

	else:
	    user1 = bot.first_name
	    user2 = curr_user

	owo_type = random.choice(("Gif", "Sticker"))
	if owo_type == "Gif":
	    try:
	        temp = random.choice(fun_strings.OWO_GIFS)
	        reply_to.reply_animation(temp)
	    except BadRequest:
	        owo_type = "Text"

	if owo_type == "Sticker":
	    try:
	        temp = random.choice(fun_strings.OWO_STICKERS)
	        reply_to.reply_sticker(temp)
	    except BadRequest:
	        owo_type = "Text"
		
		
__help__ = f"""
  ➢ `/runs`*:* reply a random string from an array of replies
  ➢ `/slap`*:* slap a user, or get slapped if not a reply
  ➢ `/shrug`*:* get shrug XD
  ➢ `/table`*:* get flip/unflip :v
  ➢ `/decide`*:* Randomly answers yes/no/maybe
  ➢ `/bluetext`*:* check urself :V
  ➢ `/roll`*:* Roll a dice
  ➢ `/rlg`*:* Join ears,nose,mouth and create an emo ;-;
  ➢ `/shout <keyword>`*:* write anything you want to give loud shout
  ➢ `/weebify <text>`*:* returns a weebified text
  ➢ `/pat`*:* pats a user, or get patted
  ➢ `/8ball`*:* predicts using 8ball method
  ➢ `/gbam`*:* troll somone with fake gbans, only Disaster People can do this
  ➢ `/cuddle`*:* cuddle someone by replying to his/her message or get cuddled
  ➢ `/hug`*:* hug someone or get hugged by {BOT_NAME}
  ➢ `/love`*:* Checks Love in your heart weather it's true or fake
  ➢ `/kiss`*:* Kiss someone or get kissed 
  ➢ `/flirt`*:* {BOT_NAME} will flirt to the replied person or with you
  ➢ `/romance`*:* {BOT_NAME} will act all romantic with you or replied person
  ➢ `/couples`*:* To Choose Couple Of The Day
  ➢ `/owo`*:* OWO de text
  ➢ `/stretch`*:* STRETCH de text
  ➢ `/clapmoji`*:* Type in reply to a message and see magic
  ➢ `/bmoji`*:* Type in reply to a message and see magic
  ➢ `/copypasta`*:* Type in reply to a message and see magic
  ➢ `/vapor`*:* owo vapor dis
  ➢ `/zalgofy`*:* reply to a message to glitch it out!
  ➢ `/abuse`*:* Abuses the cunt
  ➢ `/insult`*:* Insult the cunt
  ➢ `/react`*:* Check on your own
  ➢ `/rhappy`*:* Check on your own
  ➢ `/rangry`*:* Check on your own
  ➢ `/angrymoji`*:* Check on your own
  ➢ `/crymoji`*:* Check on your own
  ➢ `/cowsay, /tuxsay , /milksay , /kisssay , /wwwsay , /defaultsay , /bunnysay , /moosesay , /sheepsay , /rensay , /cheesesay , /ghostbusterssay , /skeletonsay <i>text</i>`*:* Returns a stylish art text from the given text
  ➢ `/deepfry`*:* Type this in reply to an image/sticker to roast the image/sticker
  ➢ `/figlet`*:* Another Style art
  ➢ `/dice`*:* Roll A dice
  ➢ `/dart`*:* Throw a dart and try your luck
  ➢ `/ball`*:* 1 to 5 any value
  ➢ `/basketball`*:* Try your luck if you can enter the ball in the ring
  ➢ `/type <text>`*:* Make the bot type something for you in a professional way
  ➢ `/carbon <text</i>`*:* Beautifies your text and enwraps inside a terminal image [ENGLISH ONLY]
  ➢ `/sticklet <text>`*:* Turn a text into a sticker
  ➢ `/fortune`*:* gets a random fortune quote
  ➢ `/quotly`*:* Type /quotly in reply to a message to make a sticker of that
  ➢ `/animate`*:* Enwrap your text in a beautiful anime
  ➢ `/dare`*:* sends random dare
  ➢ `/truth`*:* sends random truth
  ➢ `/police`*:* 🚓
"""

RUNS_HANDLER = DisableAbleCommandHandler("runs", runs, run_async=True)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, run_async=True)
PAT_HANDLER = DisableAbleCommandHandler("pat", pat, run_async=True)
ROLL_HANDLER = DisableAbleCommandHandler("roll", roll, run_async=True)
SHRUG_HANDLER = DisableAbleCommandHandler("shrug", shrug, run_async=True)
BLUETEXT_HANDLER = DisableAbleCommandHandler("bluetext", bluetext, run_async=True)
RLG_HANDLER = DisableAbleCommandHandler("rlg", rlg, run_async=True)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide, run_async=True)
TABLE_HANDLER = DisableAbleCommandHandler("table", table, run_async=True)
SHOUT_HANDLER = DisableAbleCommandHandler("shout", shout, run_async=True)
WEEBIFY_HANDLER = DisableAbleCommandHandler("weebify", weebify, run_async=True)
GBUN_HANDLER = DisableAbleCommandHandler("gbun", gbun, run_async=True)
GBAM_HANDLER = DisableAbleCommandHandler("gbam", gbam, run_async=True)
CUDDLE_HANDLER = DisableAbleCommandHandler("cuddle", cuddle, run_async=True)
FLIRT_HANDLER = DisableAbleCommandHandler("flirt", flirt, run_async=True)   
ROMANCE_HANDLER = DisableAbleCommandHandler("romance", romance, run_async=True) 
UWU_HANDLER = DisableAbleCommandHandler("uwu", uwu, run_async=True)
OWO_HANDLER = DisableAbleCommandHandler("owo", owo, run_async=True)
GDMORNING_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(goodmorning|good morning)"), goodmorning, friendly="goodmorning", run_async=True)
GDNIGHT_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(goodnight|good night)"), goodnight, friendly="goodnight", run_async=True)


dispatcher.add_handler(GBAM_HANDLER)
dispatcher.add_handler(GBUN_HANDLER)
dispatcher.add_handler(WEEBIFY_HANDLER)
dispatcher.add_handler(SHOUT_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(PAT_HANDLER)
dispatcher.add_handler(ROLL_HANDLER)
dispatcher.add_handler(SHRUG_HANDLER)
dispatcher.add_handler(BLUETEXT_HANDLER)
dispatcher.add_handler(RLG_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(TABLE_HANDLER)
dispatcher.add_handler(CUDDLE_HANDLER)
dispatcher.add_handler(FLIRT_HANDLER)
dispatcher.add_handler(ROMANCE_HANDLER)    
dispatcher.add_handler(UWU_HANDLER)
dispatcher.add_handler(OWO_HANDLER)
dispatcher.add_handler(GDMORNING_HANDLER)
dispatcher.add_handler(GDNIGHT_HANDLER)


__mod_name__ = "Fun"
__command_list__ = [
    "runs",
    "slap",
    "roll",
    "toss",
    "shrug",
    "bluetext",
    "rlg",
    "decide",
    "table",
    "pat",
    "sanitize",
    "shout",
    "weebify",
    "gbun",
    "gbam",
    "cuddle", 
    "flirt", 
    "romance", 
    "uwu", 
    "owo",
]
__handlers__ = [
    RUNS_HANDLER,
    SLAP_HANDLER,
    PAT_HANDLER,
    ROLL_HANDLER,
    TOSS_HANDLER,
    SHRUG_HANDLER,
    BLUETEXT_HANDLER,
    RLG_HANDLER,
    DECIDE_HANDLER,
    TABLE_HANDLER,
    SANITIZE_HANDLER,
    SHOUT_HANDLER,
    WEEBIFY_HANDLER,
    GBUN_HANDLER,
    GBAM_HANDLER,
    CUDDLE_HANDLER,
    FLIRT_HANDLER,
    ROMANCE_HANDLER,
    UWU_HANDLER,
    OWO_HANDLER,
    GDMORNING_HANDLER,
    GDNIGHT_HANDLER,
]
