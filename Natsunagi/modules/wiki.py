import wikipedia
from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from wikipedia.exceptions import DisambiguationError, PageError

from Natsunagi import dispatcher
from Natsunagi.modules.disable import DisableAbleCommandHandler
from Natsunagi.modules.helper_funcs.alternate import send_action, typing_action


@typing_action
def wiki(update, context):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if len(str(kueri[1])) == 0:
        update.effective_message.reply_text("Enter keywords!")
    else:
        try:
            pertama = update.effective_message.reply_text(
                "Searching the keywords from wikipedia..."
            )
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="More Information",
                            url=wikipedia.page(kueri).url,
                        )
                    ]
                ]
            )
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=pertama.message_id,
                text=wikipedia.summary(kueri, sentences=10),
                reply_markup=keyboard,
            )
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et:
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(
                f"⚠ Error\n There are too many query! Express it more!\nPossible query result:\n{eet}"
            )


WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki, run_async=True)
dispatcher.add_handler(WIKI_HANDLER)
