from fastapi import FastAPI
from telegram import __version__ as v

import Natsunagi.modules.no_sql.global_bans_db as sql1
import Natsunagi.modules.sql.blacklistusers_sql as sql2

Natsunagi = FastAPI()


@Natsunagi.get("/")
def read_root():
    return {"status": "online", "ptb_ver": v}


@Natsunagi.get("/getuser/{user_id}")
def read_item(user_id: int):
    try:
        a = sql1.is_user_gbanned(user_id)
        if a:
            user = sql1.get_gbanned_user(user_id)
            areason = user["reason"]
        else:
            areason = None

        b = sql2.is_user_blacklisted(user_id)
        if b:
            breason = sql2.get_reason(user_id)
        else:
            breason = None
        return {
            "status": "ok",
            "user_id": user_id,
            "gbanned": a,
            "gban_reason": areason,
            "blacklisted": b,
            "blacklist_reason": breason,
        }
    except Exception:
        a = None
        areason = None
        b = None
        breason = None
        return {
            "status": "ok",
            "user_id": user_id,
            "gbanned": a,
            "gban_reason": areason,
            "blacklisted": b,
            "blacklist_reason": breason,
        }
