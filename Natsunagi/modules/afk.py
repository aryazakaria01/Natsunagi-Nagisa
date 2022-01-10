import time

from telegram import MessageEntity, ParseMode
from telegram.error import BadRequest
from telegram.ext import Filters

from Natsunagi import REDIS
from Natsunagi.modules.helper_funcs.readable_time import get_readable_time
from Natsunagi.modules.helper_funcs.decorators import natsunagicmd, natsunagimsg
from Natsunagi.modules.redis.afk_redis import (
    afk_reason,
    end_afk,
    is_user_afk,
    start_afk,
)
from Natsunagi.modules.users import get_user_id

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


@natsunagicmd(command="afk", group=AFK_GROUP, can_disable=False)
@natsunagimsg((Filters.regex("(?i)^brb")), group=AFK_GROUP)
def afk(update, _):
    message = update.effective_message
    args = message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    if user.id in [777000, 1087968824]:
        return

    start_afk_time = time.time()
    reason = args[1] if len(args) >= 2 else "none"
    start_afk(user.id, reason)
    REDIS.set(f"afk_time_{user.id}", start_afk_time)
    fname = user.first_name
    try:
        message.reply_text(f"See you later 👋 <code>{fname}</code>!", parse_mode=ParseMode.HTML)
    except BadRequest:
        pass


@natsunagicmd((Filters.all & Filters.chat_type.groups), group=AFK_GROUP)
def no_longer_afk(update, _):
    user = update.effective_user
    message = update.effective_message
    if not user:  # ignore channels
        return

    if not is_user_afk(user.id):  # Check if user is afk or not
        return
    end_afk_time = get_readable_time(
        (time.time() - float(REDIS.get(f"afk_time_{user.id}")))
    )
    REDIS.delete(f"afk_time_{user.id}")
    res = end_afk(user.id)
    if res:
        if message.new_chat_members:  # dont say msg
            return
        firstname = update.effective_user.first_name
        try:
            message.reply_text(
                f"Welcome back <code>{firstname}</code>!\n\nYou were away for: <code>{end_afk_time}</code>", parse_mode=ParseMode.HTML
            )
        except BadRequest:
            return


@natsunagimsg((Filters.all & Filters.chat_type.groups & ~Filters.update.edited_message), group=AFK_REPLY_GROUP)
def reply_afk(update, context):
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        )

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            elif ent.type == MessageEntity.MENTION:
                user_id = get_user_id(
                    message.text[ent.offset : ent.offset + ent.length]
                )
                if not user_id:
                    # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                    return

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

                try:
                    chat = context.bot.get_chat(user_id)
                except BadRequest as e:
                    print(
                        "Error: Could not fetch userid {} for AFK module due to {}".format(
                            user_id, e
                        )
                    )
                    return
                fst_name = chat.first_name

            else:
                return

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update, _, user_id: int, fst_name: int, userc_id: int):
    if is_user_afk(user_id):
        reason = afk_reason(user_id)
        since_afk = get_readable_time(
            (time.time() - float(REDIS.get(f"afk_time_{user_id}")))
        )
        if int(userc_id) == int(user_id):
            return
        if reason == "none":
            res = f"<code>{fst_name}</code> is now away!\n\nLast seen: <code>{since_afk}</code>"
        else:
            res = f"<code>{fst_name}</code> is now away!\nReason: <code>{reason}</code>\n\nLast seen: <code>{since_afk}</code>"

        update.effective_message.reply_text(res, parse_mode=ParseMode.HTML)


def __gdpr__(user_id):
    end_afk(user_id)


__help__ = """
When marked as AFK, any mentions will be replied to with a message to say you're not available!

❂ /afk <reason>: Mark yourself as AFK.
❂ brb <reason>: Same as the afk command - but not a command.

An example of how to afk or brb:
`/afk dinner` or brb dinner.
"""

__mod_name__ = "AFK"
