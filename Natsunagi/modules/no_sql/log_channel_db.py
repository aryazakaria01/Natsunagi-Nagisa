from Natsunagi.modules.no_sql import get_collection


LOG_DATA = get_collection("LOG_CHANNELS")

CHANNELS = {}


def set_chat_log_channel(chat_id, log_channel):
    LOG_DATA.update_one(
        {'chat_id': chat_id},
        {"$set": {'log_channel': log_channel}},
        upsert=True
    )
    CHANNELS[str(chat_id)] = log_channel


def get_chat_log_channel(chat_id) -> int:
    return CHANNELS.get(str(chat_id))


def stop_chat_logging(chat_id) -> int:
    res = LOG_DATA.find_one_and_delete({'chat_id': chat_id})
    if str(chat_id) in CHANNELS:
        del CHANNELS[str(chat_id)]
    return res["log_channel"]


def num_logchannels() -> int:
    return LOG_DATA.count_documents({})


def migrate_chat(old_chat_id, new_chat_id):
    LOG_DATA.update_one(
        {'chat_id': old_chat_id},
        {"$set": {'chat_id': new_chat_id}}
    )
    if str(old_chat_id) in CHANNELS:
        CHANNELS[str(new_chat_id)] = CHANNELS.get(str(old_chat_id))


def __load_log_channels():
    global CHANNELS
    CHANNELS = {
        str(chat['chat_id']):str(chat['log_channel'])
        for chat in LOG_DATA.find()
        }


__load_log_channels()
