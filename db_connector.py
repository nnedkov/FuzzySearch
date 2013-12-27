#######################################
#   Filename: db_connector.py         #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Database connector '''

from config import DB_HOST

from pymongo import MongoClient



def connect_to_db():
    connection = MongoClient(DB_HOST)
    db = connection.asme

    return db


db = connect_to_db()
