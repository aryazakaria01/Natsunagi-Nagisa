import random

import requests as r
from telegram import (
    ChatAction,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.ext import CallbackContext, CommandHandler, Filters

from Natsunagi import dispatcher
from Natsunagi.modules.disable import DisableAbleCommandHandler
from Natsunagi.modules.helper_funcs.alternate import send_action, typing_action
from Natsunagi.modules.helper_funcs.chat_status import user_admin

MARKDOWN_HELP = f"""
Markdown is a very powerful formatting tool supported by telegram. {dispatcher.bot.first_name} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.
 × <code>_italic_</code>: wrapping text with '_' will produce italic text
 × <code>*bold*</code>: wrapping text with '*' will produce bold text
 × <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
 × <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
<b>Example:</b><code>[test](example.com)</code>
× <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
<b>Example:</b> <code>[This is a button](buttonurl:example.com)</code>
If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.
Keep in mind that your message <b>MUST</b> contain some text other than just a button!
"""


@user_admin
def echo(update, _):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1],
            quote=False,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!",
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)",
    )


@typing_action
def src(update, _):
    update.effective_message.reply_text(
        "Hey there! You can find what makes me click [here](https://github.com/aryazakaria01/Natsunagi-Nagisa).",
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


@send_action(ChatAction.UPLOAD_PHOTO)
def rmemes(update, context):
    msg = update.effective_message
    chat = update.effective_chat

    SUBREDS = [
        "meirl",
        "dankmemes",
        "AdviceAnimals",
        "memes",
        "meme",
        "memes_of_the_dank",
        "PornhubComments",
        "teenagers",
        "memesIRL",
        "insanepeoplefacebook",
        "terriblefacebookmemes",
    ]

    subreddit = random.choice(SUBREDS)
    res = r.get(f"https://meme-api.herokuapp.com/gimme/{subreddit}")

    if res.status_code != 200:  # Like if api is down?
        msg.reply_text("Sorry some error occurred :(")
        return
    res = res.json()

    rpage = res.get(str("subreddit"))  # Subreddit
    title = res.get(str("title"))  # Post title
    memeu = res.get(str("url"))  # meme pic url
    plink = res.get(str("postLink"))

    caps = f"× <b>Title</b>: {title}\n"
    caps += f"× <b>Subreddit:</b> <pre>r/{rpage}</pre>"

    keyb = [[InlineKeyboardButton(text="Subreddit Postlink 🔗", url=plink)]]
    try:
        context.bot.send_photo(
            chat.id,
            photo=memeu,
            caption=caps,
            reply_markup=InlineKeyboardMarkup(keyb),
            timeout=60,
            parse_mode=ParseMode.HTML,
        )

    except BadRequest as excp:
        return msg.reply_text(f"Error! {excp.message}")


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "Contact me in pm",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown help",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        ),
                    ],
                ],
            ),
        )
        return
    markdown_help_sender(update)


__help__ = """
Available commands:
*Markdown*:
❂ `/markdownhelp`: quick summary of how markdown works in telegram - can only be called in private chats

*Currency converter*:
❂ `/cash`: currency converter
Example:
× `/cash 1 USD INR`
     OR
× `/cash 1 usd inr`
» Output: `1.0 USD = 75.505 INR`

*Translator*:
❂ `/tr` or `/tl` (language code) as reply to a long message
❂ `/langs` : lists all the language codes
Example:
 × `/tr en`: translates something to english
 × `/tr hi-en`: translates hindi to english.

*Timezones*:
❂ `/time <query>`: Gives information about a timezone.
Available queries: Country Code/Country Name/Timezone Name
 × [Timezones list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

*Quotly*:
❂ `/q` : To quote a message.
❂ `/q <Number>` : To quote more than 1 messages.
❂ `/q r` : to quote a message with it's reply

Compress And Decompress: 
❂ `/zip`*:* reply to a telegram file to compress it in .zip format
❂ `/unzip`*:* reply to a telegram file to decompress it from the .zip format

*Other Commands*:
*Paste*:
❂ `/paste`*:* Saves replied content to ezup and replies with a url

*React*:
❂ `/react`*:* Reacts with a random reaction

*Urban Dictonary*:
❂ `/ud <word>`*:* Type the word or expression you want to search use

*Wikipedia*:
❂ `/wiki <query>`*:* wikipedia your query

*Wallpapers*:
❂ `/wall <query>`*:* get a wallpaper from alphacoders

*Text To Speech*:
❂ `/tts <text>`*:* Converts a text message to a voice message.
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)
SRC_HANDLER = CommandHandler(
    "source", src, filters=Filters.chat_type.private, run_async=True
)
REDDIT_MEMES_HANDLER = DisableAbleCommandHandler("rmeme", rmemes, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(SRC_HANDLER)
dispatcher.add_handler(REDDIT_MEMES_HANDLER)

__mod_name__ = "Extras"
__command_list__ = ["id", "echo", "source", "rmeme"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    SRC_HANDLER,
    REDDIT_MEMES_HANDLER,
]
