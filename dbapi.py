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
        cursor = db.strings.find({}, {'string': 1, '_id': 0})
    except:
        raise NotImplementedError

    strings = [rec['string'] for rec in cursor]

    return strings


def set_dense_index(dense_index):
    dense_index_recs = [{'_id': sid, 'string': string} for sid, string in dense_index.iteritems()]

    try:
        db.dense_index.insert(dense_index_recs)
    except:
        raise NotImplementedError


def set_inverted_index(inverted_index):
    inverted_index_recs = list()
    for length, inverted_index_len in inverted_index.iteritems():
        for qgram, sids in inverted_index_len.iteritems():
            inverted_index_recs.append({'length': length, 'qgram': qgram, 'sids': list(sids)})

    try:
        db.inverted_index.insert(inverted_index_recs)
    except:
        raise NotImplementedError
