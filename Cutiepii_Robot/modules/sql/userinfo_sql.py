import threading

from Cutiepii_Robot.modules.sql import BASE, SESSION
from sqlalchemy import Column, Integer, UnicodeText

class UserInfo(BASE):
    __tablename__ = "userinfo"
    user_id = Column(Integer, primary_key=True)
    info = Column(UnicodeText)

    def __init__(self, user_id, info):
        self.user_id = user_id
        self.info = info

    def __repr__(self):
        return "<User info %d>" % self.user_id

class UserBio(BASE):
    __tablename__ = "userbio"
    user_id = Column(Integer, primary_key=True)
    bio = Column(UnicodeText)

    def __init__(self, user_id, bio):
        self.user_id = user_id
        self.bio = bio

    def __repr__(self):
        return "<User info %d>" % self.user_id

class Rank(BASE):
    __tablename__ = "ranks"
    user_id = Column(Integer, primary_key=True)
    rank = Column(UnicodeText)

    def __init__(self, user_id, rank):
        self.user_id = user_id
        self.rank = rank

UserInfo.__table__.create(checkfirst=True)
UserBio.__table__.create(checkfirst=True)
Rank.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

def get_user_me_info(user_id):
    userinfo = SESSION.query(UserInfo).get(user_id)
    SESSION.close()
    if userinfo:
        return userinfo.info
    return None

def set_user_me_info(user_id, info):
    with INSERTION_LOCK:
        userinfo = SESSION.query(UserInfo).get(user_id)
        if userinfo:
            userinfo.info = info
        else:
            userinfo = UserInfo(user_id, info)
        SESSION.add(userinfo)
        SESSION.commit()

def get_user_bio(user_id):
    userbio = SESSION.query(UserBio).get(user_id)
    SESSION.close()
    if userbio:
        return userbio.bio
    return None

def set_user_bio(user_id, bio):
    with INSERTION_LOCK:
        userbio = SESSION.query(UserBio).get(user_id)
        if userbio:
            userbio.bio = bio
        else:
            userbio = UserBio(user_id, bio)

        SESSION.add(userbio)
        SESSION.commit()

def get_rank(user_id):
    ranks = SESSION.query(Rank).get(user_id)
    SESSION.close()
    if ranks:
        return ranks.rank
    return None
       
def set_rank(user_id, rank):
    with INSERTION_LOCK:
        ranks = SESSION.query(Rank).get(user_id)
        if ranks:
            ranks.rank = rank
        else:
            ranks = Rank(user_id, rank)

        SESSION.add(ranks)
        SESSION.commit()
