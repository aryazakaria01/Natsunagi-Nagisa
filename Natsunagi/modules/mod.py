# Credits by moezilla
# Take it from Yone and SungJinWoo
# Ported by moezilla and aryazakaria01

import html

from telegram import ParseMode
from telegram.error import BadRequest
from telegram.utils.helpers import mention_html

import Natsunagi.modules.sql.mod_sql as sql
from Natsunagi import dispatcher
from Natsunagi.modules.disable import DisableAbleCommandHandler
from Natsunagi.modules.helper_funcs.chat_status import user_admin
from Natsunagi.modules.helper_funcs.extraction import extract_user
from Natsunagi.modules.log_channel import loggable


@loggable
@user_admin
def mod(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("No need to Modertor an Admin!")
        return ""
    if sql.is_modd(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) is already moderator in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.mod(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) has been moderator in {chat_title}",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MODERATOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
def dismod(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("This Is User Admin")
        return ""
    if not sql.is_modd(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} isn't moderator yet!")
        return ""
    sql.dismod(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} is no longer moderator in {chat_title}."
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNMODERTOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
def modd(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are Moderator.\n"
    modd_users = sql.list_modd(message.chat_id)
    for i in modd_users:
        member = chat.get_member(int(i.user_id))
        msg += f"{member.user['first_name']}\n"
    if msg.endswith("moderator.\n"):
        message.reply_text(f"No users are Moderator in {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def modr(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    if sql.is_modd(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} is an moderator user.")
    else:
        message.reply_text(f"{member.user['first_name']} is not an moderator user.")


__help__ = """
Sometimes, you don't trust but want to make user manager of your group then you can make him/her moderator.
Maybe not enough to make them admin, but you might be ok with ban, mute, and warn not.
That's what modcheck are for - mod of trustworthy users to allow to manage your group.
*Admin Commands*:
❂ `/addmod`*:* Add moderator to the user. 
❂ `/rmmod`*:* Remove the moderator access from user.
❂ `/modcheck`*:* Check a user's modcheck status in this chat.
❂ `/modlist`*:* List all mod users list.
"""

ADDMOD = DisableAbleCommandHandler("addmod", mod, run_async=True)
RMMOD = DisableAbleCommandHandler("rmmod", dismod, run_async=True)
MODLIST = DisableAbleCommandHandler("modlist", modd, run_async=True)
MODCHECK = DisableAbleCommandHandler("modcheck", modr, run_async=True)

dispatcher.add_handler(ADDMOD)
dispatcher.add_handler(RMMOD)
dispatcher.add_handler(MODLIST)
dispatcher.add_handler(MODCHECK)

__mod_name__ = "Moderation"

__command_list__ = ["addmod", "rmmod", "modlist", "modcheck"]
__handlers__ = [ADDMOD, RMMOD, MODLIST, MODCHECK]
