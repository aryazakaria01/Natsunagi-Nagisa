import html
import importlib
import json
import re
import time
import traceback
from platform import python_version
from sys import argv
from typing import Optional

from pyrogram import __version__ as pyr
from telegram import (
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    User,
)
from telegram import __version__ as tgl
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import CallbackContext, Filters
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlh

import Natsunagi.modules.no_sql.users_db as user_db
from Natsunagi import (
    BOT_USERNAME,
    CERT_PATH,
    DONATION_LINK,
    HELP_IMG,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    StartTime,
    dispatcher,
    pgram,
    telethn,
    updater,
)
from Natsunagi.modules import ALL_MODULES
from Natsunagi.modules.helper_funcs.alternate import typing_action
from Natsunagi.modules.helper_funcs.chat_status import is_user_admin
from Natsunagi.modules.helper_funcs.decorators import (
    natsunagicallback,
    natsunagicmd,
    natsunagimsg,
)
from Natsunagi.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


HELP_MSG = "Click the button below to get help manu in your pm."
HELP_MSG_MODULES = "Contact me in PM to get help of {}"
START_MSG = "I'm awake already!\n<b>Haven't slept since:</b> <code>{}</code>"

PM_START_TEXT = """
Hello {}, My name is {}, and i'm here for you![.](https://telegra.ph/file/cd1ff43d08d42cdd93ab5.jpg)
────────────────────────
❂ I'm an anime-themed group management bot with an Tantei wa mou, shindeiru theme.
❂ Maintenance by @Badboyanim
────────────────────────
❂ Click the button /help below to see how to use me.
"""

GROUP_START_TEXT = """
I'm awake already!
Haven't slept since: {}
"""

buttons = [
    [InlineKeyboardButton(text="About Me", callback_data="natsunagi_")],
    [
        InlineKeyboardButton(text="❓ Help", callback_data="help_back"),
        InlineKeyboardButton(text="📢 Updates", url="https://t.me/CyberMusicProject"),
    ],
    [
        InlineKeyboardButton(
            text=f"Add Natsunagi to your group",
            url=f"t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
]


HELP_STRINGS = """
*Main commands available*[:](https://telegra.ph/file/a8ce80707def6b27d254f.jpg)
 ➛ /help: PM's you this message.
 ➛ /help <module name>: PM's you info about that module.
 ➛ /donate: information on how to donate!
 ➛ /settings:
   × in PM: will send you your settings for all supported modules.
   × in a group: will redirect you to pm, with all that chat's settings.
"""

DONATE_STRING = """× I'm Free for Everyone ×"""


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Natsunagi.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


@natsunagicmd(command="test")
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@natsunagicmd(command="start", pass_args=True)
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Back To Home", callback_data="help_back"
                                )
                            ]
                        ]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(context.bot.first_name),
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_text(
            f"<b>Hi I'm Natsunagi Nagisa!</b>\n<b>Started working since:</b> <code>{uptime}</code>",
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update, context):
    """#TODO
    Params:
        update  -
        context -
    """
    try:
        raise context.error
    except (Unauthorized, BadRequest):
        pass
        # remove update.message.chat_id from conversation list
    except TimedOut:
        pass
        # handle slow connection problems
    except NetworkError:
        pass
        # handle other connection problems
    except ChatMigrated:
        pass
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        pass
        # handle all other telegram related errors


@natsunagicallback(pattern=r"help_")
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "╔━⊰✦✪「 *{}* module: 」✪✦⊱━╗\n".format(HELPABLE[module].__mod_name__)
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


@natsunagicallback(pattern=r"natsunagi_")
def natsunagi_about_callback(update, context):
    query = update.callback_query
    if query.data == "natsunagi_":
        query.message.edit_text(
            text="❂ I'm *Natsunagi Nagisa*, a powerful group management bot built to help you manage your group easily.\n"
            "\n× I can restrict users."
            "\n× I can greet users with customizable welcome messages and even set a group's rules."
            "\n× I have an advanced anti-flood system."
            "\n× I can warn users until they reach max warns, with each predefined actions such as ban, mute, kick, etc."
            "\n× I have a note keeping system, blacklists, and even predetermined replies on certain keywords."
            "\n× I check for admins' permissions before executing any command and more stuffs"
            "\n\n_Natsunagu's licensed under the GNU General Public License v3.0_"
            "\n\n Click on button bellow to get basic help for Natsunagi Nagisa.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Admins", callback_data="natsunagi_admin"
                        ),
                        InlineKeyboardButton(
                            text="Notes", callback_data="natsunagi_notes"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Support", callback_data="natsunagi_support"
                        ),
                        InlineKeyboardButton(
                            text="Credits", callback_data="natsunagi_credit"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Valkyrie Family", url="https://t.me/valkyriefamily"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Go Back", callback_data="natsunagi_back"
                        ),
                    ],
                ]
            ),
        )
    elif query.data == "natsunagi_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
            PM_START_TEXT.format(
                escape_markdown(first_name),
                escape_markdown(uptime),
                user_db.num_users(),
                user_db.num_chats(),
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )

    elif query.data == "natsunagi_admin":
        query.message.edit_text(
            text=f"*❂ Let's make your group bit effective now*\n"
            "\nCongragulations, Natsunagi Nagisa now ready to manage your group."
            "\n\n*Admin Tools*"
            "\nBasic Admin tools help you to protect and powerup your group."
            "\nYou can ban members, Kick members, Promote someone as admin through commands of bot."
            "\n\n*Greetings*"
            "\nLets set a welcome message to welcome new users coming to your group."
            "\nsend `/setwelcome [message]` to set a welcome message!",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Go Back", callback_data="natsunagi_")]]
            ),
        )

    elif query.data == "natsunagi_notes":
        query.message.edit_text(
            text=f"<b>❂ Setting up notes</b>"
            f"\nYou can save message/media/audio or anything as notes"
            f"\nto get a note simply use # at the beginning of a word"
            f"\n\nYou can also set buttons for notes and filters (refer help menu)",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Go Back", callback_data="natsunagi_")]]
            ),
        )
    elif query.data == "natsunagi_support":
        query.message.edit_text(
            text="*❂ Natsunagi support chats*"
            "\nJoin My Support Group/Channel for see or report a problem on Natsunagi.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Support", url="t.me/NatsunagiCorporationGroup"
                        ),
                        InlineKeyboardButton(
                            text="Updates", url="https://t.me/CyberMusicProject"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Go Back", callback_data="natsunagi_"
                        ),
                    ],
                ]
            ),
        )

    elif query.data == "natsunagi_credit":
        query.message.edit_text(
            text=f"❂ Credis for Natsunagi\n"
            "\nHere Developers Making And Give Inspiration For Made The Natsunagi Nagisa",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="sena-ex", url="https://github.com/kennedy-ex"
                        ),
                        InlineKeyboardButton(
                            text="TheHamkerCat", url="https://github.com/TheHamkerCat"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Feri", url="https://github.com/FeriEXP"
                        ),
                        InlineKeyboardButton(
                            text="riz-ex", url="https://github.com/riz-ex"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Anime Kaizoku", url="https://github.com/animekaizoku"
                        ),
                        InlineKeyboardButton(
                            text="TheGhost Hunter", url="https://github.com/HuntingBots"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Inuka Asith", url="https://github.com/inukaasith"
                        ),
                        InlineKeyboardButton(
                            text="Noob-Kittu", url="https://github.com/noob-kittu"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Queen Arzoo", url="https://github.com/QueenArzoo"
                        ),
                        InlineKeyboardButton(
                            text="Paul Larsen", url="https://github.com/PaulSonOfLars"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Ryomen-Sukuna", url="https://github.com/Ryomen-Sukuna"
                        ),
                        InlineKeyboardButton(
                            text="UserLazy", url="https://github.com/UserLazy"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="zYxDevs", url="https://github.com/zYxDevs"
                        ),
                        InlineKeyboardButton(
                            text="idzero23", url="https://github.com/idzero23"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Tonic990", url="https://github.com/Tonic990"
                        ),
                        InlineKeyboardButton(
                            text="aryazakaria01", url="https://github.com/aryazakaria01"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Go Back", callback_data="natsunagi_"
                        ),
                    ],
                ]
            ),
        )


def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text="❂ This advance command for Musicplayer."
            "\n\n❂ Command for admins only."
            "\n × `/pause` - To pause the playback."
            "\n × `/resume` - To resuming the playback You've paused."
            "\n × `/skip` - To skipping the player."
            "\n × `/end` - For end the playback."
            "\n\n❂ Command for all members."
            "\n × `/play` <query /reply audio> - Playing music via YouTube.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Go Back", callback_data="natsunagi_")]]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(
                escape_markdown(first_name),
                escape_markdown(uptime),
                sql.num_users(),
                sql.num_chats(),
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )


@typing_action
@natsunagicmd(command="help")
def get_help(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:

        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_photo(
                HELP_IMG,
                HELP_MSG_MODULES.format(module.capitalize()),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Open In Private Chat",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username,
                                    module,
                                ),
                            ),
                        ],
                    ],
                ),
            )
            return
        update.effective_message.reply_photo(
            HELP_IMG,
            HELP_MSG,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Open In Private Chat",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            " 〔 *{}* 〕\n".format(HELPABLE[module].__mod_name__)
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Go Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    elif CHAT_SETTINGS:
        chat_name = dispatcher.bot.getChat(chat_id).title
        dispatcher.bot.send_message(
            user_id,
            text="Which module would you like to check {}'s settings for?".format(
                chat_name
            ),
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
            ),
        )
    else:
        dispatcher.bot.send_message(
            user_id,
            "Seems like there aren't any chat settings available :'(\nSend this "
            "in a group chat you're admin in to find its current settings!",
            parse_mode=ParseMode.MARKDOWN,
        )


@natsunagicallback(pattern=r"stngs_")
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@natsunagicmd(command="settings")
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type == chat.PRIVATE:
        send_settings(chat.id, user.id, True)

    elif is_user_admin(chat, user.id):
        text = "Click here to get this chat's settings, as well as yours."
        msg.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Settings",
                            url="t.me/{}?start=stngs_{}".format(
                                context.bot.username, chat.id
                            ),
                        )
                    ]
                ]
            ),
        )
    else:
        text = "Click here to check your settings."


@natsunagicmd(command="donate")
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1138045685:
            update.effective_message.reply_text(
                "I'm free for everyone ❤️ If you wanna make me smile, just join"
                "[My Channel]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


@natsunagimsg((Filters.status_update.migrate))
def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        try:
            mod.__migrate__(old_chat, new_chat)
        except BaseException:
            pass  # Some sql modules make errors.

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(
                f"@{SUPPORT_CHAT}",
                f"""**Natsunagi Nagisa Started!**

» Python: `{python_version()}`
» Telethon: `{tlh}`
» Pyrogram: `{pyr}`
» Telegram Library: v`{tgl}`""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info(
            f"Natsunagi started, Using webhook. | BOT: [@{dispatcher.bot.username}]"
        )
        updater.start_webhook(listen="127.0.0.1", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info(
            f"Natsunagi started, Using long polling. | BOT: [@{dispatcher.bot.username}]"
        )
        updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            timeout=15,
            read_latency=4,
            drop_pending_updates=True,
        )
    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()
    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Natsunagi successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pgram.start()
    main()
