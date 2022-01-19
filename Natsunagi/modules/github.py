from distutils import command
import aiohttp
import html
from pyrogram import filters
from typing import Optional, List

import Natsunagi.modules.helper_funcs.git_api as api
import Natsunagi.modules.sql.github_sql as sql

from Natsunagi import pgram, OWNER_ID, DEV_USERS, DEMONS, dispatcher
from Natsunagi.utils.errors import capture_err
from Natsunagi.modules.helper_funcs.filters import CustomFilters
from Natsunagi.modules.helper_funcs.chat_status import user_admin
from Natsunagi.modules.helper_funcs.decorators import natsunagicmd
from Natsunagi.modules.helper_funcs.misc import delete
from Natsunagi.modules.disable import DisableAbleCommandHandler

from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    RegexHandler,
    run_async,
)

from telegram import (
    Message,
    Chat,
    Update,
    Bot,
    User,
    ParseMode,
    InlineKeyboardMarkup,
    MAX_MESSAGE_LENGTH,
)

__mod_name__ = "Github"


@pgram.on_message(filters.command("github"))
@capture_err
async def github(_, message):
    if len(message.command) != 2:
        await message.reply_text("/git Username")
        return
    username = message.text.split(None, 1)[1]
    URL = f"https://api.github.com/users/{username}"
    async with aiohttp.ClientSession() as session, session.get(URL) as request:
        if request.status == 404:
            return await message.reply_text("404")

        result = await request.json()
        try:
            url = result["html_url"]
            name = result["name"]
            company = result["company"]
            bio = result["bio"]
            created_at = result["created_at"]
            avatar_url = result["avatar_url"]
            blog = result["blog"]
            location = result["location"]
            repositories = result["public_repos"]
            followers = result["followers"]
            following = result["following"]
            caption = f"""**Info Of {name}**
**Username:** `{username}`
**Bio:** `{bio}`
**Profile Link:** [Here]({url})
**Company:** `{company}`
**Created On:** `{created_at}`
**Repositories:** `{repositories}`
**Blog:** `{blog}`
**Location:** `{location}`
**Followers:** `{followers}`
**Following:** `{following}`"""
        except Exception as e:
            print(str(e))
    await message.reply_photo(photo=avatar_url, caption=caption)


def getphh(index):
    recentRelease = api.getReleaseData(api.getData("phhusson/treble_experimentations"), index)
    if recentRelease is None:
        return "The specified release could not be found"
    author = api.getAuthor(recentRelease)
    authorUrl = api.getAuthorUrl(recentRelease)
    name = api.getReleaseName(recentRelease)
    assets = api.getAssets(recentRelease)
    releaseName = api.getReleaseName(recentRelease)
    message = "<b>Author:</b> <a href='{}'>{}</a>\n".format(authorUrl, author)
    message += "<b>Release Name:</b> <code>"+releaseName+"</code>\n\n"
    message += "<b>Assets:</b>\n"
    for asset in assets:
        fileName = api.getReleaseFileName(asset)
        if fileName in ("manifest.xml", "patches.zip"):
            continue
        fileURL = api.getReleaseFileURL(asset)
        assetFile = "× <a href='{}'>{}</a>".format(fileURL, fileName)
        sizeB = ((api.getSize(asset))/1024)/1024
        size = "{0:.2f}".format(sizeB)
        message += assetFile + "\n"
        message += "    <code>Size: "  + size + " MB</code>\n"
    return message


def getData(url, index):
    if not api.getData(url):
        return "Invalid <user>/<repo> combo"
    recentRelease = api.getReleaseData(api.getData(url), index)
    if recentRelease is None:
        return "The specified release could not be found"
    author = api.getAuthor(recentRelease)
    authorUrl = api.getAuthorUrl(recentRelease)
    name = api.getReleaseName(recentRelease)
    assets = api.getAssets(recentRelease)
    releaseName = api.getReleaseName(recentRelease)
    message = "*Author:* [{}]({})\n".format(author, authorUrl)
    message += "*Release Name:* " + releaseName + "\n\n"
    for asset in assets:
        message += "*Asset:* \n"
        fileName = api.getReleaseFileName(asset)
        fileURL = api.getReleaseFileURL(asset)
        assetFile = "[{}]({})".format(fileName, fileURL)
        sizeB = ((api.getSize(asset)) / 1024) / 1024
        size = "{0:.2f}".format(sizeB)
        downloadCount = api.getDownloadCount(asset)
        message += assetFile + "\n"
        message += "Size: " + size + " MB"
        message += "\nDownload Count: " + str(downloadCount) + "\n\n"
    return message


# likewise, aux function, not async
def getRepo(bot, update, reponame):
    chat_id = update.effective_chat.id
    repo = sql.get_repo(str(chat_id), reponame)
    if repo:
        return repo.value, repo.backoffset
    return None, None


@natsunagicmd(command="git", admin_ok=True)
def getRelease(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    msg = update.effective_message
    if len(args) == 0:
        msg.reply_text("Please use some arguments!")
        return
    if (
        len(args) != 1
        and not (len(args) == 2 and args[1].isdigit())
        and not ("/" in args[0])
    ):
        deletion(update, context, msg.reply_text("Please specify a valid combination of <user>/<repo>"))
        return
    index = 0
    if len(args) == 2:
        index = int(args[1])
    url = args[0]
    text = getData(url, index)
    deletion(update, context, msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True))
    return


# def hashFetch(update: Update, context: CallbackContext):  # kanged from notes
#     bot, args = context.bot, context.args
#     message = update.effective_message.text
#     msg = update.effective_message
#     fst_word = message.split()[0]
#     no_hash = fst_word[1:]
#     url, index = getRepo(bot, update, no_hash)
#     if url is None and index is None:
#         deletion(update, context, msg.reply_text(
#             "There was a problem parsing your request. Likely this is not a saved repo shortcut",
#             parse_mode=ParseMode.MARKDOWN,
#             disable_web_page_preview=True,
#         ))
#         return
#     text = getData(url, index)
#     deletion(update, context, msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True))
#     return


@natsunagicmd(command="fetch", admin_ok=True)
def cmdFetch(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    msg = update.effective_message
    if len(args) != 1:
        deletion(update, context, msg.reply_text("Invalid repo name"))
        return
    url, index = getRepo(bot, update, args[0])
    if url is None and index is None:
        deletion(update, context, msg.reply_text(
            "There was a problem parsing your request. Likely this is not a saved repo shortcut",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        ))
        return
    text = getData(url, index)
    deletion(update, context, msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True))
    return


@natsunagicmd(command="changelog", admin_ok=True)
def changelog(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    msg = update.effective_message
    if len(args) != 1:
        deletion(update, context, msg.reply_text("Invalid repo name"))
        return
    url, index = getRepo(bot, update, args[0])
    if not api.getData(url):
        msg.reply_text("Invalid <user>/<repo> combo")
        return
    data = api.getData(url)
    release = api.getReleaseData(data, index)
    body = api.getBody(release)
    deletion(update, context, msg.reply_text(body))
    return


@natsunagicmd(command="saverepo")
@user_admin
def saveRepo(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat_id = update.effective_chat.id
    msg = update.effective_message
    if (
        len(args) != 2
        and (len(args) != 3 and not args[2].isdigit())
        or not ("/" in args[1])
    ):
        deletion(update, context, msg.reply_text("Invalid data, use <reponame> <user>/<repo> <value (optional)>"))
        return
    index = 0
    if len(args) == 3:
        index = int(args[2])
    sql.add_repo_to_db(str(chat_id), args[0], args[1], index)
    deletion(update, context, msg.reply_text("Repo shortcut saved successfully!"))
    return


@natsunagicmd(command="delrepo")
@user_admin
def delRepo(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat_id = update.effective_chat.id
    msg = update.effective_message
    if len(args) != 1:
        msg.reply_text("Invalid repo name!")
        return
    sql.rm_repo(str(chat_id), args[0])
    deletion(update, context, msg.reply_text("Repo shortcut deleted successfully!"))
    return


@natsunagicmd(command="listrepo", admin_ok=True)
def listRepo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    chat = update.effective_chat
    chat_name = chat.title or chat.first_name or chat.username
    repo_list = sql.get_all_repos(str(chat_id))
    msg = "*List of repo shotcuts in {}:*\n"
    des = "You can get repo shortcuts by using `/fetch repo`, or `&repo`.\n"
    for repo in repo_list:
        repo_name = " × `{}`\n".format(repo.name)
        if len(msg) + len(repo_name) > MAX_MESSAGE_LENGTH:
            deletion(update, context, update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN))
            msg = ""
        msg += repo_name
    if msg == "*List of repo shotcuts in {}:*\n":
        deletion(update, context, update.effective_message.reply_text("No repo shortcuts in this chat!"))
    elif len(msg) != 0:
        deletion(update, context, update.effective_message.reply_text(
            msg.format(chat_name) + des, parse_mode=ParseMode.MARKDOWN
        ))

@natsunagicmd(command="gitver", admin_ok=True)
def getVer(update: Update, context: CallbackContext):
    msg = update.effective_message
    ver = api.vercheck()
    deletion(update, context, msg.reply_text("GitHub API version: " + ver))
    return


def deletion(update: Update, context: CallbackContext, delmsg):
    chat = update.effective_chat
    cleartime = get_clearcmd(chat.id, "github")

    if cleartime:
        context.dispatcher.run_async(delete, delmsg, cleartime.time)