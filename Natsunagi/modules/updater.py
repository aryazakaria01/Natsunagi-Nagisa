import asyncio
import sys
import shlex
from datetime import datetime
from os import environ, execle, path, remove
from typing import Tuple

import heroku3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pyrogram.types import Message

from Natsunagi import Config
from Natsunagi.modules.helper_funcs.decorators import natsunagicmd
from Natsunagi.helper_func.logger_s import LogIt

REPO_ = Config.UPSTREAM_REPO
BRANCH_ = Config.U_BRANCH


@natsunagicmd(command="update")
async def update_it(client, message):
    engine = message.Engine
    msg_ = await edit_or_reply(message, engine.get_string("UPDATING_PLS_WAIT"))
    try:
        repo = Repo()
    except GitCommandError:
        return await msg_.edit(
            engine.get_string("INVALID_GIT_CMD")
        )
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "upstream" in repo.remotes:
            origin = repo.remote("upstream")
        else:
            origin = repo.create_remote("upstream", REPO_)
        origin.fetch()
        repo.create_head(Config.U_BRANCH, origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    if repo.active_branch.name != Config.U_BRANCH:
        return await msg_.edit(
            engine.get_sring("CUSTOM_BRANCH").format(repo.active_branch.name, Config.U_BRANCH)
        )
    try:
        repo.create_remote("upstream", REPO_)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(Config.U_BRANCH)
    if not Config.HEROKU_URL:
        try:
            ups_rem.pull(Config.U_BRANCH)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await run_cmd("pip3 install --no-cache-dir -r requirements.txt")
        await msg_.edit(engine.get_string("UPDATED"))
        args = [sys.executable, "-m", "main_startup"]
        execle(sys.executable, *args, environ)
        exit()
        return
    else:
        await msg_.edit(engine.get_string("HEROKU_DETECTED"))
        ups_rem.fetch(Config.U_BRANCH)
        repo.git.reset("--hard", "FETCH_HEAD")
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(Config.HEROKU_URL)
        else:
            remote = repo.create_remote("heroku", Config.HEROKU_URL)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except BaseException as error:
            await msg_.edit(f"**Updater Error** \nTraceBack : `{error}`")
            return repo.__del__()


async def run_cmd(cmd: str) -> Tuple[str, str, int, int]:
    """Run Commands"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def edit_or_reply(message, text, parse_mode="md"):
    sudo_lis_t = await sudo_list()
    """Edit Message If Its From Self, Else Reply To Message, (Only Works For Sudo's)"""
    if not message:
        return await message.edit(text, parse_mode=parse_mode)
    if not message.from_user:
        return await message.edit(text, parse_mode=parse_mode)
    if message.from_user.id in sudo_lis_t:
        if message.reply_to_message:
            return await message.reply_to_message.reply_text(text, parse_mode=parse_mode)
        return await message.reply_text(text, parse_mode=parse_mode)
    return await message.edit(text, parse_mode=parse_mode)


def get_text(message: Message) -> [None, str]:
    """Extract Text From Commands"""
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None
