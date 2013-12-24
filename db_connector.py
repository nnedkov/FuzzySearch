#######################################
#   Filename: db_connector.py         #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Database connector '''

from pymongo import MongoClient



def connect_to_db():
    connection_str = 'mongodb://localhost'
    connection = MongoClient(connection_str)
    return connection.asme


db = connect_to_db()