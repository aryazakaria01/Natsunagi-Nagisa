from distutils import command
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from hurry.filesize import size as sizee
from requests import get
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import BadRequest
from ujson import loads
from yaml import load, Loader

from Natsunagi import dispatcher
from Natsunagi.modules.sql.clear_cmd_sql import get_clearcmd
from Natsunagi.modules.github import getphh
from Natsunagi.modules.disable import DisableAbleCommandHandler
from Natsunagi.modules.helper_funcs.alternate import typing_action
from Natsunagi.modules.helper_funcs.misc import delete
from Natsunagi.modules.helper_funcs.decorators import natsunagicmd

GITHUB = "https://github.com"
DEVICES_DATA = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"


@natsunagicmd(command="magisk", can_disable=True)
@typing_action
def magisk(update, _):
    url = "https://raw.githubusercontent.com/topjohnwu/magisk-files/"
    releases = ""
    for types, branch in {
        "Stable": ["master/stable", "master"],
        "Canary": ["master/canary", "canary"],
    }.items():
        data = get(url + branch[0] + ".json").json()
        if types != "Canary":
            releases += (
                f"*{types}*: \n"
                f'× App - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["magisk"]["link"]}) - ['
                f'Changelog]({data["magisk"]["note"]})\n \n'
            )
        else:
            releases += (
                f"*{types}*: \n"
                f'× App - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["magisk"]["link"]}) - ['
                f'Changelog]({data["magisk"]["note"]})\n'
                f"\n Now magisk is packed as all in one, "
                f"refer [this installation](https://topjohnwu.github.io/Magisk/install.html) procedure for more info.\n"
            )

    update.message.reply_text(
        "*Latest Magisk Releases:*\n\n{}".format(releases),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


@natsunagicmd(command="device", can_disable=True)
@typing_action
def device(update, context):
    args = context.args
    if len(args) == 0:
        reply = "No codename provided, write a codename for fetching informations."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    devices = " ".join(args)
    db = get(DEVICES_DATA).json()
    newdevice = devices.strip("lte") if devices.startswith("beyond") else devices
    try:
        reply = f"Search results for {devices}:\n\n"
        brand = db[newdevice][0]["brand"]
        name = db[newdevice][0]["name"]
        model = db[newdevice][0]["model"]
        codename = newdevice
        reply += (
            f"<b>{brand} {name}</b>\n"
            f"Model: <code>{model}</code>\n"
            f"Codename: <code>{codename}</code>\n\n"
        )
    except KeyError:
        reply = f"Couldn't find info about {devices}!\n"
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    update.message.reply_text(
        "{}".format(reply), parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


@natsunagicmd(command="twrp", can_disable=True)
@typing_action
def twrp(update, context):
    args = context.args
    if len(args) == 0:
        reply = "No codename provided, write a codename for fetching informations."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return

    _device = " ".join(args)
    url = get(f"https://eu.dl.twrp.me/{_device}/")
    if url.status_code == 404:
        reply = f"Couldn't find twrp downloads for {_device}!\n"
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    else:
        reply = f"*Latest Official TWRP for {_device}*\n"
        db = get(DEVICES_DATA).json()
        newdevice = _device.strip("lte") if _device.startswith("beyond") else _device
        try:
            brand = db[newdevice][0]["brand"]
            name = db[newdevice][0]["name"]
            reply += f"*{brand} - {name}*\n"
        except KeyError:
            pass
        page = BeautifulSoup(url.content, "lxml")
        date = page.find("em").text.strip()
        reply += f"*Updated:* {date}\n"
        trs = page.find("table").find_all("tr")

        # find latest version
        base_ver = (0, 0, 0)
        idx = 0
        for i, tag in enumerate(trs):
            dl_path = tag.find("a")["href"]
            match = re.search(r"([\d.]+)", dl_path)
            new_ver = tuple(int(x) for x in match.group(1).split("."))
            if new_ver > base_ver:
                base_ver = new_ver
                idx = i

        download = trs[idx].find("a")
        dl_link = f"https://eu.dl.twrp.me{download['href']}"
        dl_file = download.text
        size = trs[idx].find("span", {"class": "filesize"}).text
        reply += f"[{dl_file}]({dl_link}) - {size}\n"

        update.message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


# Picked from AstrakoBot; Thanks to them!
@natsunagicmd(command="orangefox", can_disable=True)
@typing_action
def orangefox(update, _):
    message = update.effective_message
    devices = message.text[len("/orangefox ") :]
    btn = ""

    if devices:
        link = get(
            f"https://api.orangefox.download/v3/releases/?codename={devices}&sort=date_desc&limit=1"
        )

        if link.status_code == 404:
            msg = f"OrangeFox recovery is not avaliable for {devices}"
        else:
            page = loads(link.content)
            file_id = page["data"][0]["_id"]
            link = get(
                f"https://api.orangefox.download/v3/devices/get?codename={devices}"
            )
            page = loads(link.content)
            oem = page["oem_name"]
            model = page["model_name"]
            full_name = page["full_name"]
            maintainer = page["maintainer"]["username"]
            link = get(f"https://api.orangefox.download/v3/releases/get?_id={file_id}")
            page = loads(link.content)
            dl_file = page["filename"]
            build_type = page["type"]
            version = page["version"]
            changelog = page["changelog"][0]
            size = str(round(float(page["size"]) / 1024 / 1024, 1)) + "MB"
            dl_link = page["mirrors"]["DL"]
            date = datetime.fromtimestamp(page["date"])
            md5 = page["md5"]
            msg = f"*Latest OrangeFox Recovery for the {full_name}*\n\n"
            msg += f"× Manufacturer: `{oem}`\n"
            msg += f"× Model: `{model}`\n"
            msg += f"× Codename: `{devices}`\n"
            msg += f"× Build type: `{build_type}`\n"
            msg += f"× Maintainer: `{maintainer}`\n"
            msg += f"× Version: `{version}`\n"
            msg += f"× Changelog: `{changelog}`\n"
            msg += f"× Size: `{size}`\n"
            msg += f"× Date: `{date}`\n"
            msg += f"× File: `{dl_file}`\n"
            msg += f"× MD5: `{md5}`\n"
            btn = [[InlineKeyboardButton(text="Download", url=dl_link)]]
    else:
        msg = "Enter the device codename to fetch, like:\n`/orangefox mido`"

    update.message.reply_text(
        text=msg,
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


# Picked from UserIndoBot; Thanks to them!
@natsunagicmd(command="los", can_disable=True)
@typing_action
def los(update, context) -> str:
    message = update.effective_message
    args = context.args
    try:
        device = args[0]
    except Exception:
        device = ""

    if device == "":
        reply_text = "*Please Type Your Device Codename*\nExample : `/los lavender`"
        message.reply_text(
            reply_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    fetch = get(f"https://download.lineageos.org/api/v1/{device}/nightly/*")
    if fetch.status_code == 200 and len(fetch.json()["response"]) != 0:
        usr = fetch.json()
        data = len(usr["response"]) - 1  # the latest rom are below
        response = usr["response"][data]
        filename = response["filename"]
        url = response["url"]
        buildsize_a = response["size"]
        buildsize_b = sizee(int(buildsize_a))
        version = response["version"]

        reply_text = f"*Download :* [{filename}]({url})\n"
        reply_text += f"*Build Size :* `{buildsize_b}`\n"
        reply_text += f"*Version :* `{version}`\n"

        keyboard = [
            [InlineKeyboardButton(text="Click Here To Downloads", url=f"{url}")]
        ]
        message.reply_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return
    message.reply_text(
        "`Couldn't find any results matching your query.`",
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


@natsunagicmd(command="gsi", can_disable=True)
@typing_action
def gsi(update, context):
    message = update.effective_message

    usr = get(
        "https://api.github.com/repos/phhusson/treble_experimentations/releases/latest"
    ).json()
    reply_text = "*Gsi'S Latest release*\n"
    for i in range(len(usr)):
        try:
            name = usr["assets"][i]["name"]
            url = usr["assets"][i]["browser_download_url"]
            reply_text += f"[{name}]({url})\n"
        except IndexError:
            continue
    message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)


@natsunagicmd(command="bootleg", can_disable=True)
@typing_action
def bootleg(update, context) -> str:
    message = update.effective_message
    args = context.args
    try:
        codename = args[0]
    except Exception:
        codename = ""

    if codename == "":
        message.reply_text(
            "*Please Type Your Device Codename*\nExample : `/bootleg lavender`",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    fetch = get("https://bootleggersrom-devices.github.io/api/devices.json")
    if fetch.status_code == 200:
        data = fetch.json()

        if codename.lower() == "x00t":
            device = "X00T"
        elif codename.lower() == "rmx1971":
            device = "RMX1971"
        else:
            device = codename.lower()

        try:
            fullname = data[device]["fullname"]
            filename = data[device]["filename"]
            buildate = data[device]["buildate"]
            buildsize = data[device]["buildsize"]
            buildsize = sizee(int(buildsize))
            downloadlink = data[device]["download"]
            if data[device]["mirrorlink"] != "":
                mirrorlink = data[device]["mirrorlink"]
            else:
                mirrorlink = None
        except KeyError:
            message.reply_text(
                "`Couldn't find any results matching your query.`",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            return

        reply_text = f"*BootlegersROM for {fullname}*\n"
        reply_text += f"*Download :* [{filename}]({downloadlink})\n"
        reply_text += f"*Size :* `{buildsize}`\n"
        reply_text += f"*Build Date :* `{buildate}`\n"
        if mirrorlink is not None:
            reply_text += f"[Mirror link]({mirrorlink})"

        keyboard = [
            [
                InlineKeyboardButton(
                    text="Click Here To Downloads", url=f"{downloadlink}"
                )
            ]
        ]

        message.reply_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    if fetch.status_code == 404:
        message.reply_text(
            "`Couldn't reach api`",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return


@natsunagicmd(command='checkfw', can_disable=True)
def checkfw(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    
    if len(args) == 2:
        temp, csc = args
        model = f'sm-' + temp if not temp.upper().startswith('SM-') else temp
        fota = get(
            f'http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml'
        )

        if fota.status_code != 200:
            msg = f"Couldn't check for {temp.upper()} and {csc.upper()}, please refine your search or try again later!"

        else:
            page = BeautifulSoup(fota.content, 'lxml')
            os = page.find("latest").get("o")

            if page.find("latest").text.strip():
                msg = f'*Latest released firmware for {model.upper()} and {csc.upper()} is:*\n'
                pda, csc, phone = page.find("latest").text.strip().split('/')
                msg += f'× PDA: `{pda}`\n× CSC: `{csc}`\n'
                if phone:
                    msg += f'× Phone: `{phone}`\n'
                if os:
                    msg += f'× Android: `{os}`\n'
                msg += ''
            else:
                msg = f'*No public release found for {model.upper()} and {csc.upper()}.*\n\n'

    else:
        msg = 'Give me something to fetch, like:\n`/checkfw SM-N975F DBT`'

    delmsg = message.reply_text(
        text = msg,
        parse_mode = ParseMode.MARKDOWN,
        disable_web_page_preview = True,
    )

    cleartime = get_clearcmd(chat.id, "checkfw")

    if cleartime:
        context.dispatcher.run_async(delete, delmsg, cleartime.time)


@natsunagicmd(command='getfw', can_disable=True)
def getfw(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    btn = ""
    
    if len(args) == 2:
        temp, csc = args
        model = f'sm-' + temp if not temp.upper().startswith('SM-') else temp
        fota = get(
            f'http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml'
        )

        if fota.status_code != 200:
            msg = f"Couldn't check for {temp.upper()} and {csc.upper()}, please refine your search or try again later!"

        else:
            url1 = f'https://samfrew.com/model/{model.upper()}/region/{csc.upper()}/'
            url2 = f'https://www.sammobile.com/samsung/firmware/{model.upper()}/{csc.upper()}/'
            url3 = f'https://sfirmware.com/samsung-{model.lower()}/#tab=firmwares'
            url4 = f'https://samfw.com/firmware/{model.upper()}/{csc.upper()}/'
            fota = get(
                f'http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml'
            )
            page = BeautifulSoup(fota.content, 'lxml')
            os = page.find("latest").get("o")
            msg = ""
            if page.find("latest").text.strip():
                pda, csc2, phone = page.find("latest").text.strip().split('/')
                msg += f'*Latest firmware for {model.upper()} and {csc.upper()} is:*\n'
                msg += f'× PDA: `{pda}`\n× CSC: `{csc2}`\n'
                if phone:
                    msg += f'× Phone: `{phone}`\n'
                if os:
                    msg += f'× Android: `{os}`\n'
            msg += '\n'
            msg += f'*Downloads for {model.upper()} and {csc.upper()}*\n'
            btn = [[InlineKeyboardButton(text=f"samfrew.com", url = url1)]]
            btn += [[InlineKeyboardButton(text=f"sammobile.com", url = url2)]]
            btn += [[InlineKeyboardButton(text=f"sfirmware.com", url = url3)]]
            btn += [[InlineKeyboardButton(text=f"samfw.com", url = url4)]]
    else:
        msg = 'Give me something to fetch, like:\n`/getfw SM-N975F DBT`'

    delmsg = message.reply_text(
        text = msg,
        reply_markup = InlineKeyboardMarkup(btn),
        parse_mode = ParseMode.MARKDOWN,
        disable_web_page_preview = True,
    )

    cleartime = get_clearcmd(chat.id, "getfw")

    if cleartime:
        context.dispatcher.run_async(delete, delmsg, cleartime.time)


@natsunagicmd(command='phh', can_disable=True)
def phh(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    index = int(args[0]) if len(args) > 0 and args[0].isdigit() else 0
    text = getphh(index)

    delmsg = message.reply_text(
        text,
        parse_mode = ParseMode.HTML,
        disable_web_page_preview = True,
    )

    cleartime = get_clearcmd(chat.id, "phh")

    if cleartime:
        context.dispatcher.run_async(delete, delmsg, cleartime.time)


@natsunagicmd(command='miui', can_disable=True)
def miui(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    device = message.text[len("/miui ") :]
    markup = []

    if device:
        link = "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/miui-updates-tracker/master/data/latest.yml"
        yaml_data = load(get(link).content, Loader=Loader)
        data = [i for i in yaml_data if device in i['codename']]

        if not data:
            msg = f"Miui is not avaliable for {device}"
        else:
            for fw in data:
                av = fw['android']
                branch = fw['branch']
                method = fw['method']
                link = fw['link']
                fname = fw['name']
                version = fw['version']
                size = fw['size']
                btn = fname + ' | ' + branch + ' | ' + method + ' | ' + version + ' | ' + av + ' | ' + size
                markup.append([InlineKeyboardButton(text = btn, url = link)])

            device = fname.split(" ")
            device.pop()
            device = " ".join(device)
            msg = f"The latest firmwares for the *{device}* are:"
    else:
        msg = 'Give me something to fetch, like:\n`/miui whyred`'

    delmsg = message.reply_text(
        text = msg,
        reply_markup = InlineKeyboardMarkup(markup),
        parse_mode = ParseMode.MARKDOWN,
        disable_web_page_preview = True,
    )

    cleartime = get_clearcmd(chat.id, "miui")

    if cleartime:
        context.dispatcher.run_async(delete, delmsg, cleartime.time)


__help__ = """
Get the latest Magsik releases or TWRP for your device!
*Android related commands:*
× /magisk - Gets the latest magisk release for Stable/Beta/Canary.
× /device <codename> - Gets android device basic info from its codename.
× /twrp <codename> -  Gets latest twrp for the android device using the codename.
× /orangefox <codename> -  Gets latest orangefox recovery for the android device using the codename.
× /los <codename> - Gets Latest los build.
× /miui <devicecodename>- Fetches latest firmware info for a given device codename
× /phh : Get lastest phh builds from github
× /checkfw <model> <csc> - Samsung only - Shows the latest firmware info for the given device, taken from samsung servers
× /getfw <model> <csc> - Samsung only - gets firmware download links from samfrew, sammobile and sfirmwares for the given device
"""

__mod_name__ = "Android"
