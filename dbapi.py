#######################################
#   Filename: indexer.py              #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Database interface '''

from db_connector import db



def get_all_strings():
    try:
        cursor = db.strings.find({}, {'string': 1})
    except:
        raise Exception()

    return [string for string in cursor]


def set_dense_index(dense_index):
    dense_index_recs = [{'_id': sid, 'string': string} for sid, string in dense_index]

    try:
        db.dense_index.insert(dense_index_recs)
    except:
        raise Exception()
