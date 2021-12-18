import threading

from sqlalchemy import Boolean, Column, String

from Natsunagi.modules.sql import BASE, SESSION


class CleanLinked(BASE):
    __tablename__ = "clean_linked"
    chat_id = Column(String(14), primary_key=True)
    status = Column(Boolean, default=False)

    def __init__(self, chat_id, status):
        self.chat_id = str(chat_id)
        self.status = status


CleanLinked.__table__.create(checkfirst=True)

CLEANLINKED_LOCK = threading.RLock()


def getCleanLinked(chat_id):
    try:
        resultObj = SESSION.query(CleanLinked).get(str(chat_id))
        if resultObj:
            return resultObj.status
        return False  # default
    finally:
        SESSION.close()


def setCleanLinked(chat_id, status):
    with CLEANLINKED_LOCK:
        prevObj = SESSION.query(CleanLinked).get(str(chat_id))
        if prevObj:
            SESSION.delete(prevObj)
        newObj = CleanLinked(str(chat_id), status)
        SESSION.add(newObj)
        SESSION.commit()
