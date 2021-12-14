import re
import os
import subprocess
import sys
import asyncio
import html

from Natsunagi import (
    dispatcher,
    DEV_USERS,
    telethn,
    OWNER_ID,
)
from Natsunagi.modules.helper_funcs.chat_status import dev_plus

from contextlib import suppress
from statistics import mean
from time import monotonic as time
from time import sleep
from telegram import (
    TelegramError,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from telegram.error import Unauthorized
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    run_async,
)
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telethon import events


def leave_cb(update: Update, context: CallbackContext):
    bot = context.bot
    callback = update.callback_query
    if callback.from_user.id != DEV_USERS:
        callback.answer(text="This isn't for you", show_alert=True)
        return

    match = re.match(r"leavechat_cb_\((.+?)\)", callback.data)
    chat = int(match.group(1))
    bot.leave_chat(chat_id=chat)
    callback.answer(text="Left the chat from this group.")


@dev_plus
def allow_groups(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        state = "Lockdown is " + "on" if not Natsunagi.ALLOW_CHATS else "off"
        update.effective_message.reply_text(f"Current state: {state}")
        return
    if args[0].lower() in ["off", "no"]:
        Natsunagi.ALLOW_CHATS = True
    elif args[0].lower() in ["yes", "on"]:
        Natsunagi.ALLOW_CHATS = False
    else:
        update.effective_message.reply_text("Format: /lockdown Yes/No or Off/On")
        return
    update.effective_message.reply_text("Done! Lockdown value toggled.")


class Store:
    def __init__(self, func):
        self.func = func
        self.calls = []
        self.time = time()
        self.lock = asyncio.Lock()

    def average(self):
        return round(mean(self.calls), 2) if self.calls else 0

    def __repr__(self):
        return f"<Store func={self.func.__name__}, average={self.average()}>"

    async def __call__(self, event):
        async with self.lock:
            if not self.calls:
                self.calls = [0]
            if time() - self.time > 1:
                self.time = time()
                self.calls.append(1)
            else:
                self.calls[-1] += 1
        await self.func(event)


async def nothing(event):
    pass


messages = Store(nothing)
inline_queries = Store(nothing)
callback_queries = Store(nothing)

telethn.add_event_handler(messages, events.NewMessage())
telethn.add_event_handler(inline_queries, events.InlineQuery())
telethn.add_event_handler(callback_queries, events.CallbackQuery())


@telethn.on(events.NewMessage(pattern=r"/getstats", from_users=OWNER_ID))
async def getstats(event):
    await event.reply(
        f"Natsunagi Event Statistics\n"
        f"» Average messages: <code>{messages.average()}<code>/s\n"
        f"» Average Callback Queries: <code>{callback_queries.average()}<code>/s\n"
        f"» Average Inline Queries: <code>{inline_queries.average()}<code>/s",
        parse_mode=ParseMode.HTML,
    )


@dev_plus
def pip_install(update: Update, context: CallbackContext):
    message = update.effective_message
    args = context.args
    if not args:
        message.reply_text("Enter a package name.")
        return
    if len(args) >= 1:
        cmd = "py -m pip install {}".format(" ".join(args))
        process = subprocess.Popen(
            cmd.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        reply = ""
        stderr = stderr.decode()
        stdout = stdout.decode()
        if stdout:
            reply += f"*Stdout*\n`{stdout}`\n"
        if stderr:
            reply += f"*Stderr*\n`{stderr}`\n"

        message.reply_text(text=reply, parse_mode=ParseMode.MARKDOWN)


@dev_plus
def leave(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args
    if args:
        chat_id = str(args[0])
        leave_msg = " ".join(args[1:])
        try:
            context.bot.send_message(chat_id, leave_msg)
            bot.leave_chat(int(chat_id))
            update.effective_message.reply_text("Left chat.")
        except TelegramError:
            update.effective_message.reply_text("Failed to leave chat for some reason.")
    else:
        chat = update.effective_chat
        # user = update.effective_user
        natsunagi_leave_bt = [
            [
                InlineKeyboardButton(
                    text="Yes", callback_data="leavechat_cb_({})".format(chat.id)
                ),
                InlineKeyboardButton(text="No", callback_data="close2"),
            ]
        ]
        update.effective_message.reply_text(
            "I'm going to leave {}, press the button below to confirm".format(
                chat.title
            ),
            reply_markup=InlineKeyboardMarkup(natsunagi_leave_bt),
        )


close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("No", callback_data="close2")]]
)


@dev_plus
def gitpull(update: Update, context: CallbackContext):
    sent_msg = update.effective_message.reply_text(
        "Pulling all changes from remote and then attempting to restart."
    )
    subprocess.Popen("git pull", stdout=subprocess.PIPE)

    sent_msg_text = sent_msg.text + "\n\nChanges pulled...I guess.. Restarting in "

    for i in reversed(range(5)):
        sent_msg.edit_text(sent_msg_text + str(i + 1))
        sleep(1)

    sent_msg.edit_text("Restarted.")

    os.system("restart.bat")
    os.execv("start.bat", sys.argv)


@dev_plus
def restart(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Exiting all Processes and starting a new Instance!"
    )
    process = subprocess.run("pkill python3 && python3 -m Natsunagi", check=True)
    process.communicate()


PIP_INSTALL_HANDLER = CommandHandler("install", pip_install, run_async=True)
LEAVE_HANDLER = CommandHandler("leave", leave, run_async=True)
GITPULL_HANDLER = CommandHandler("gitpull", gitpull, run_async=True)
RESTART_HANDLER = CommandHandler("reboot", restart, run_async=True)
ALLOWGROUPS_HANDLER = CommandHandler("lockdown", allow_groups, run_async=True)
LEAVE_CALLBACK_HANDLER = CallbackQueryHandler(
    leave_cb, pattern=r"leavechat_cb_", run_async=True
)

dispatcher.add_handler(PIP_INSTALL_HANDLER)
dispatcher.add_handler(ALLOWGROUPS_HANDLER)
dispatcher.add_handler(LEAVE_HANDLER)
dispatcher.add_handler(GITPULL_HANDLER)
dispatcher.add_handler(RESTART_HANDLER)
dispatcher.add_handler(LEAVE_CALLBACK_HANDLER)

__mod_name__ = "Dev"
__handlers__ = [
    LEAVE_HANDLER,
    GITPULL_HANDLER,
    RESTART_HANDLER,
    ALLOWGROUPS_HANDLER,
    LEAVE_CALLBACK_HANDLER,
    PIP_INSTALL_HANDLER,
]
