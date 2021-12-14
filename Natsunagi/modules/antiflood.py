import html
import re

from typing import Optional, List
from telegram import (
    Message,
    Chat,
    Update,
    Bot,
    User,
    ChatPermissions,
)
from telegram.error import BadRequest
from telegram.ext import (
    Filters,
    MessageHandler,
    CommandHandler,
    run_async,
    CallbackContext,
)
from telegram.utils.helpers import mention_html, escape_markdown

from Natsunagi import dispatcher, DRAGONS, DEV_USERS, SUDO_USERS
from Natsunagi.modules.helper_funcs.string_handling import extract_time
from Natsunagi.modules.helper_funcs.chat_status import is_user_admin
from Natsunagi.modules.log_channel import loggable
from Natsunagi.modules.sql import antiflood_sql as sql
from Natsunagi.modules.connection import connected
from Natsunagi.modules.redis.approvals_redis import is_approved
from ..modules.helper_funcs.anonymous import user_admin, AdminPerms
from Natsunagi.modules.helper_funcs.alternate import send_message, typing_action
from Natsunagi.modules.helper_funcs.decorators import (
    natsunagicmd,
    natsunagimsg,
    natsunagicallback,
)

FLOOD_GROUP = 3


@loggable
def check_flood(update, context) -> Optional[str]:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]

    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return

    if not user:  # ignore channels
        return ""

    # ignore admins
    if is_user_admin(chat, user.id):
        sql.update_flood(chat.id, None)
        return ""

    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban:
        return ""

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            chat.ban_member(user.id)
            execstrings = "Banned"
            tag = "BANNED"
        elif getmode == 2:
            chat.ban_member(user.id)
            chat.unban_member(user.id)
            execstrings = "Kicked"
            tag = "KICKED"
        elif getmode == 3:
            context.bot.restrict_chat_member(
                chat.id, user.id, permissions=ChatPermissions(can_send_messages=False)
            )
            execstrings = "Muted"
            tag = "MUTED"
        elif getmode == 4:
            bantime = extract_time(msg, getvalue)
            chat.ban_member(user.id, until_date=bantime)
            execstrings = "Banned for {}".format(getvalue)
            tag = "TBAN"
        elif getmode == 5:
            mutetime = extract_time(msg, getvalue)
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                until_date=mutetime,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = "Muted for {}".format(getvalue)
            tag = "TMUTE"
        send_message(
            update.effective_message,
            "Wanna Spam?! Sorry it's not your house Man!\n{}!".format(execstrings),
        )

        return (
            "<b>{}:</b>"
            "\n#{}"
            "\n<b>User:</b> {}"
            "\nFlooded the group.".format(
                html.escape(chat.title), tag, mention_html(user.id, user.first_name)
            )
        )

    except BadRequest:
        msg.reply_text(
            "I can't restrict people here, give me permissions first! Until then, I'll disable anti-flood."
        )
        sql.set_flood(chat.id, 0)
        return (
            "<b>{}:</b>"
            "\n#INFO"
            "\nDon't have enough permission to restrict users so automatically disabled anti-flood".format(
                chat.title
            )
        )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
@typing_action
def set_flood(update, context) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "This command is meant to use in group not in PM",
            )
            return ""
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if len(args) >= 1:
        val = args[0].lower()
        if val in ("off", "no", "0"):
            sql.set_flood(chat_id, 0)
            if conn:
                text = message.reply_text(
                    "Antiflood has been disabled in {}.".format(chat_name)
                )
            else:
                text = message.reply_text("Antiflood has been disabled.")
            send_message(update.effective_message, text, parse_mode="markdown")

        elif val.isdigit():
            amount = int(val)
            if amount <= 0:
                sql.set_flood(chat_id, 0)
                if conn:
                    text = message.reply_text(
                        "Antiflood has been disabled in {}.".format(chat_name)
                    )
                else:
                    text = message.reply_text("Antiflood has been disabled.")
                return (
                    "<b>{}:</b>"
                    "\n#SETFLOOD"
                    "\n<b>Admin:</b> {}"
                    "\nDisable antiflood.".format(
                        html.escape(chat_name), mention_html(user.id, user.first_name)
                    )
                )

            if amount < 3:
                send_message(
                    update.effective_message,
                    "Antiflood must be either 0 (disabled) or number greater than 3!",
                )
                return ""
            sql.set_flood(chat_id, amount)
            if conn:
                text = message.reply_text(
                    "Anti-flood has been set to {} in chat: {}".format(
                        amount, chat_name
                    )
                )
            else:
                text = message.reply_text(
                    "Successfully updated anti-flood limit to {}!".format(amount)
                )
            send_message(update.effective_message, text, parse_mode="markdown")
            return (
                "<b>{}:</b>"
                "\n#SETFLOOD"
                "\n<b>Admin:</b> {}"
                "\nSet antiflood to <code>{}</code>.".format(
                    html.escape(chat_name),
                    mention_html(user.id, user.first_name),
                    amount,
                )
            )

        else:
            message.reply_text("Invalid argument please use a number, 'off' or 'no'")
    else:
        message.reply_text(
            (
                "Use `/setflood number` to enable anti-flood.\nOr use `/setflood off` to disable antiflood!."
            ),
            parse_mode="markdown",
        )
    return ""


@typing_action
def flood(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "This command is meant to use in group not in PM",
            )
            return
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        if conn:
            text = msg.reply_text(
                "I'm not enforcing any flood control in {}!".format(chat_name)
            )
        else:
            text = msg.reply_text("I'm not enforcing any flood control here!")
    elif conn:
        text = msg.reply_text(
            "I'm currently restricting members after {} consecutive messages in {}.".format(
                limit, chat_name
            )
        )
    else:
        text = msg.reply_text(
            "I'm currently restricting members after {} consecutive messages.".format(
                limit
            )
        )
    send_message(update.effective_message, text, parse_mode="markdown")


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
@typing_action
def set_flood_mode(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "This command is meant to use in group not in PM",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() == "ban":
            settypeflood = "ban"
            sql.set_flood_strength(chat_id, 1, "0")
        elif args[0].lower() == "kick":
            settypeflood = "kick"
            sql.set_flood_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeflood = "mute"
            sql.set_flood_strength(chat_id, 3, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode tban <timevalue>`.
    Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "tban for {}".format(args[1])
            sql.set_flood_strength(chat_id, 4, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode tmute <timevalue>`.
    Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "tmute for {}".format(args[1])
            sql.set_flood_strength(chat_id, 5, str(args[1]))
        else:
            send_message(
                update.effective_message, "I only understand ban/kick/mute/tban/tmute!"
            )
            return
        if conn:
            text = msg.reply_text(
                "Exceeding consecutive flood limit will result in {} in {}!".format(
                    settypeflood, chat_name
                )
            )
        else:
            text = msg.reply_text(
                "Exceeding consecutive flood limit will result in {}!".format(
                    settypeflood
                )
            )
        send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>Admin:</b> {}\n"
            "Has changed antiflood mode. User will {}.".format(
                settypeflood,
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
            )
        )
    getmode, getvalue = sql.get_flood_setting(chat.id)
    if getmode == 1:
        settypeflood = "ban"
    elif getmode == 2:
        settypeflood = "kick"
    elif getmode == 3:
        settypeflood = "mute"
    elif getmode == 4:
        settypeflood = "tban for {}".format(getvalue)
    elif getmode == 5:
        settypeflood = "tmute for {}".format(getvalue)
    if conn:
        text = msg.reply_text(
            "Sending more messages than flood limit will result in {} in {}.".format(
                settypeflood, chat_name
            )
        )
    else:
        text = msg.reply_text(
            "Sending more message than flood limit will result in {}.".format(
                settypeflood
            )
        )
    send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        return "Not enforcing to flood control."
    return "Antiflood has been set to`{}`.".format(limit)


__help__ = """
You know how sometimes, people join, send 100 messages, and ruin your chat? With antiflood, that happens no more!
Antiflood allows you to take action on users that send more than x messages in a row. Exceeding the set flood \
will result in restricting that user.
 - /flood: Get the current flood control setting
*Admin only*:
 - /setflood <int/'no'/'off'>: enables or disables flood control
 - /setfloodmode <ban/kick/mute/tban/tmute> <value>: Action to perform when user have exceeded flood limit. ban/kick/mute/tmute/tban
 Note:
 - Value must be filled for tban and tmute!
 It can be:
 5m = 5 minutes
 6h = 6 hours
 3d = 3 days
 1w = 1 week
 """

__mod_name__ = "Anti-Flood"

FLOOD_BAN_HANDLER = MessageHandler(
    Filters.all & ~Filters.status_update & Filters.chat_type.groups,
    check_flood,
    run_async=True,
)
SET_FLOOD_HANDLER = CommandHandler(
    "setflood", set_flood, pass_args=True, run_async=True
)  # , filters=Filters.chat_type.groups)
SET_FLOOD_MODE_HANDLER = CommandHandler(
    "setfloodmode", set_flood_mode, pass_args=True, run_async=True
)  # , filters=Filters.chat_type.groups)
FLOOD_HANDLER = CommandHandler(
    "flood", flood, run_async=True
)  # , filters=Filters.chat_type.groups)

dispatcher.add_handler(FLOOD_BAN_HANDLER, FLOOD_GROUP)
dispatcher.add_handler(SET_FLOOD_HANDLER)
dispatcher.add_handler(SET_FLOOD_MODE_HANDLER)
dispatcher.add_handler(FLOOD_HANDLER)
