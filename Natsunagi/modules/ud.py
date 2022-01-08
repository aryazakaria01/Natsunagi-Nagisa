from requests import get
from telegram import ParseMode

from Natsunagi import dispatcher
from Natsunagi.modules.disable import DisableAbleCommandHandler
from Natsunagi.modules.helper_funcs.alternate import typing_action
from Natsunagi.modules.helper_funcs.decorators import natsunagicmd

@natsunagicmd(command="ud")
@typing_action
def ud(update, context):
    msg = update.effective_message
    args = context.args
    text = " ".join(args).lower()
    if not text:
        msg.reply_text("<code>Please enter keywords to search on ud!</code>", parse_mode=ParseMode.HTML)
        return
    if text == "Arya":
        msg.reply_text("Arya is my owner so if you search him on urban dictionary you can't find the meaning because he is my husband and only me who know what's the meaning of Arya!")
        return
    try:
        results = get(f"http://api.urbandictionary.com/v0/define?term={text}").json()
        reply_text = f"Word: <code>{text}</code>\n\nDefinition: \n<code>{results["list"][0]["definition"]}</code>", parse_mode=ParseMode.HTML
        reply_text += f"\n\nExample: \n<code>{results["list"][0]["example"]}</code>", parse_mode=ParseMode.HTML
    except IndexError:
        reply_text = (
            f"Word: <code>{text}</code>\n\nResults: <code>Sorry could not find any matching results!</code>", parse_mode=ParseMode.HTML
        )
    ignore_chars = "[]"
    reply = reply_text
    for chars in ignore_chars:
        reply = reply.replace(chars, "")
    if len(reply) >= 4096:
        reply = reply[:4096]  # max msg lenth of tg.
    try:
        msg.reply_text(reply)
    except BadRequest as err:
        msg.reply_text(f"Error! <code>{err.message}</code>", parse_mode=ParseMode.HTML)