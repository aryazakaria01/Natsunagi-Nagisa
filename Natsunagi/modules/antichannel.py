import html

import requests
from telegram import TelegramError, Update
from telegram.ext import CallbackContext
from telegram.ext.filters import Filters

import Natsunagi.modules.sql.antilinkedchannel_sql as sql
from Natsunagi import TOKEN, dispatcher
from Natsunagi.modules.disable import DisableAbleCommandHandler
from Natsunagi.modules.helper_funcs.anonymous import AdminPerms, user_admin
from Natsunagi.modules.helper_funcs.chat_status import bot_admin
from Natsunagi.modules.helper_funcs.chat_status import user_admin as u_admin
from Natsunagi.modules.helper_funcs.decorators import natsunagimsg
from Natsunagi.modules.sql import acm_sql


@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
def antilinkedchannel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on"]:
            sql.enable(chat.id)
            message.reply_html(
                "Enabled anti linked channel in {}".format(html.escape(chat.title))
            )
        elif s in ["off", "no"]:
            sql.disable(chat.id)
            message.reply_html(
                "Disabled anti linked channel in {}".format(html.escape(chat.title))
            )
        else:
            message.reply_text("Unrecognized arguments {}".format(s))
        return
    message.reply_html(
        "Linked channel deletion is currently {} in {}".format(
            sql.status(chat.id), html.escape(chat.title)
        )
    )


@natsunagimsg(Filters.is_automatic_forward, group=111)
def eliminate_linked_channel_msg(update: Update, _: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    if not sql.status(chat.id):
        return
    try:
        message.delete()
    except TelegramError:
        return


@bot_admin
@u_admin
def antichannelmode(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    msg = update.effective_message
    if args:
        if len(args) != 1:
            msg.reply_text("Invalid arguments!")
            return
        param = args[0]
        if param in ("on", "true", "yes", "On", "Yes", "True"):
            acm_sql.setCleanLinked(chat.id, True)
            msg.reply_text(
                f"*Enabled* Anti channel in {chat.title}. Messages sent by channel will be deleted.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        elif param in ("off", "false", "no", "No", "Off", "False"):
            acm_sql.setCleanLinked(chat.id, False)
            msg.reply_text(
                f"*Disabled* Anti channel in {chat.title}.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        else:
            msg.reply_text(
                "Your input was not recognised as one of: yes/no/on/off"
            )  # on or off ffs
            return
    else:
        stat = acm_sql.getCleanLinked(str(chat.id))
        if stat:
            msg.reply_text(
                f"Linked channel post deletion is currently *enabled* in {chat.title}. Messages sent from the linked channel will be deleted.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        else:
            msg.reply_text(
                f"Linked channel post deletion is currently *disabled* in {chat.title}.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return


# Ban all channel of that user and delete the channel sent message
# Credits To -> https://t.me/ShalmonAnandMate and https://github.com/TamimZaman99 and https://github.com/aryazakaria01
# This Module is made by Shalmon. Do Not Edit this part !!
def sfachat(update: Update, context: CallbackContext):
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot = context.bot
    if user and user.id == 136817688:
        cleanlinked = acm_sql.getCleanLinked(str(chat.id))
        if cleanlinked:
            linked_group_channel = bot.get_chat(chat.id)
            lgc_id = linked_group_channel.linked_chat_id
            if str(update.message.sender_chat.id) == str(lgc_id):
                return ""
            BAN_CHAT_CHANNEL = f"https://api.telegram.org/bot{TOKEN}/banChatSenderChat?chat_id={update.message.chat.id}&sender_chat_id={update.message.sender_chat.id}"
            respond = requests.post(BAN_CHAT_CHANNEL)
            if respond.status_code == 200:
                BANNED_CHANNEL_LINK = (
                    f"t.me/c/{update.message.sender_chat.id}/1".replace("-100", "")
                )
                update.message.reply_text(
                    f"""
• AUTO-BAN CHANNEL EVENT ‼️
🚫 Banned This Channel: <a href="{BANNED_CHANNEL_LINK}">here's the link</a>
                """,
                    parse_mode=ParseMode.HTML,
                )
            else:
                update.message.reply_text(
                    f"""
There was an error occured during auto ban and delete message. please report this to @BlackKnightsUnion_DevChat.
• Error: `{respond}`
                """
                )
            msg.delete()
            return ""


__mod_name__ = "AntiChannel"

__help__ = """
*Anti Channel Mode*:
❂ `/antichannelmode` or `/antichannel`*:* Bans and deletes anyone who tries to talk as channel and forces them to talk using real account
❂ `/antilinkedchannel`*:* Makes Natsunagi Nagisa automatically delete linked channel posts from groups
"""

CLEANLINKED_HANDLER = CommandHandler(
    ["acm", "antichannel", "antichannelmode"],
    antichannelmode,
    filters=Filters.chat_type.groups,
    run_async=True,
)
SFA_HANDLER = MessageHandler(Filters.all, sfachat, allow_edit=True, run_async=True)

ANTILINKEDCHANNEL_HANDLER = DisableAbleCommandHandler(
    "antilinkedchat", antilinkedchannel, run_async=True
)

dispatcher.add_handler(SFA_HANDLER, group=69)
dispatcher.add_handler(CLEANLINKED_HANDLER)
dispatcher.add_handler(ANTILINKEDCHANNEL_HANDLER, group=112)

__command_list__ = [
    "antichannel",
    "antilinkedchat",
]

__handlers__ = [
    CLEANLINKED_HANDLER,
    SFA_HANDLER,
    ANTILINKEDCHANNEL_HANDLER,
]
