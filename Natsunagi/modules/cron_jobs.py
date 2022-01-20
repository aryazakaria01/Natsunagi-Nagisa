import os
import shutil
import datetime
import subprocess
from time import sleep

from telegram.update import Update
from telegram.ext.filters import Filters
from telegram.ext.callbackcontext import CallbackContext

from Natsunagi import DB_URL, OWNER_ID, DEV_USERS, dispatcher, LOGGER, BACKUP_PASS
from Natsunagi.modules.helper_funcs.decorators import natsunagicmd


@natsunagicmd(
    command="backupdb", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID)
)
def backup_now(_: Update, ctx: CallbackContext):
    cronjob.run(dispatcher=dispatcher)


@natsunagicmd(
    command="stopjobs", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID)
)
def stop_jobs(update: Update, _: CallbackContext):
    print(j.stop())
    update.effective_message.reply_text("Scheduler has been shut down")


@natsunagicmd(
    command="startjobs", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID)
)
def start_jobs(update: Update, _: CallbackContext):
    print(j.start())
    update.effective_message.reply_text("Scheduler started")


zip_pass = BACKUP_PASS


def backup_db(_: CallbackContext):
    bot = dispatcher.bot
    tmpmsg = "Performing backup, Please wait..."
    tmp = bot.send_message(OWNER_ID, tmpmsg)
    datenow = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dbbkpname = "db_{}_{}.tar".format(bot.username, datenow)
    bkplocation = "backups/{}".format(datenow)
    bkpcmd = "pg_dump {} --format=tar > {}/{}".format(DB_URL, bkplocation, dbbkpname)

    if not os.path.exists(bkplocation):
        os.makedirs(bkplocation)
    LOGGER.info("Performing db backup")
    loginfo = "db backup"
    term(bkpcmd, loginfo)
    if not os.path.exists("{}/{}".format(bkplocation, dbbkpname)):
        bot.send_message(OWNER_ID, "An error occurred during the db backup")
        tmp.edit_text("Backup Failed!")
        sleep(8)
        tmp.delete()
        return
    else:
        LOGGER.info("Copying config, and logs to backup location")
        if os.path.exists("logs.txt"):
            print("Logs copied")
            shutil.copyfile("logs.txt", "{}/logs.txt".format(bkplocation))
        if os.path.exists("config.ini"):
            print("Config copied")
            shutil.copyfile("config.ini", "{}/config.ini".format(bkplocation))
        LOGGER.info("Zipping the backup")
        zipcmd = "zip --password '{}' {} {}/*".format(
            zip_pass, bkplocation, bkplocation
        )
        zipinfo = "zipping db backup"
        LOGGER.info("Zip initiated")
        term(zipcmd, zipinfo)
        LOGGER.info("Zip done")
        sleep(1)
        with open("backups/{}".format(f"{datenow}.zip"), "rb") as bkp:
            nm = "{} backup \n".format(bot.username) + datenow
            bot.send_document(OWNER_ID, document=bkp, caption=nm, timeout=20)
        LOGGER.info("Removing zipped files")
        shutil.rmtree("backups/{}".format(datenow))
        LOGGER.info("Backup done")
        tmp.edit_text("Backup complete!")
        sleep(5)
        tmp.delete()


@natsunagicmd(
    command="purgebackups", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID)
)
def del_bkp_fldr(update: Update, _: CallbackContext):
    shutil.rmtree("backups")
    update.effective_message.reply_text("'Backups' directory has been purged!")


def term(cmd, info):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    stdout, stderr = process.communicate()
    stderr = stderr.decode()
    stdout = stdout.decode()
    if stdout:
        LOGGER.info(f"{info} successful!")
        LOGGER.info(f"{stdout}")
    if stderr:
        LOGGER.error(f"error while running {info}")
        LOGGER.info(f"{stderr}")


from Natsunagi import updater as u

# run the backup daily at 1:00
twhen = datetime.datetime.strptime("01:00", "%H:%M").time()
j = u.job_queue
cronjob = j.run_daily(callback=backup_db, name="database backups", time=twhen)
