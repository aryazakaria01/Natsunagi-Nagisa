from sqlalchemy import Column, String

from Natsunagi.module.sql import BASE, SESSION


class database(BASE):
    __tablename__ = "subsplease"
    website = Column(String, primary_key=True)
    link = Column(String)

    def __init__(self, website, link):
        self.website = website
        self.link = link


database.__table__.create(checkfirst=True)


def get(website):
    try:
        return SESSION.query(database).get(website)
    except:
        return None
    finally:
        SESSION.close()


def update(website, link):
    adder = SESSION.query(database).get(website)
    if adder:
        adder.link = link
    else:
        adder = database(website, link)
    SESSION.add(adder)
    SESSION.commit()
