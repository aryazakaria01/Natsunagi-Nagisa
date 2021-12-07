"""MongoDB Database."""

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from pymongo import MongoClient, collection

from Natsunagi import MONGO_URI, MONGO_DB, MONGO_PORT

# MongoDB Client
mongodb = MongoClient(MONGO_DB_URL, 27017)[MONGO_DB]
motor = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)
db = motor[MONGO_DB]
engine = AIOEngine(motor, MONGO_DB)
DB_CLIENT = MongoClient(MONGO_URI)
_DB = DB_CLIENT["Natsunagi"]


def get_collection(name: str) -> collection:
    """Get the collection from database."""
    return _DB[name]
