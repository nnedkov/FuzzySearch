#######################################
#   Filename: db_connector.py         #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Database connector '''

from pymongo import MongoClient
from config import DB_HOST



def connect_to_db():
    connection = MongoClient(DB_HOST)
    return connection.asme


db = connect_to_db()