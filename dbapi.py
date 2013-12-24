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
            sids = list(sids)
            # TODO: check if with serialization/deserialization is faster
            inverted_index_recs.append({'length': length, 'qgram': qgram, 'cardinality': len(sids), 'sids': sids})

    try:
        db.inverted_index.insert(inverted_index_recs)
    except:
        raise NotImplementedError


def asme_is_in_operation():
        return True


def get_inverted_lists(length, qgrams):
    inverted_lists = list()
    for qgram in qgrams:
        try:
            cursor = db.inverted_index.find({'length': length, 'qgram': qgram}, {'sids': 1, 'cardinality': 1, '_id': 0})
            inverted_list = [inv_list for inv_list in cursor]
            assert len(inverted_list) in [0, 1]
            if len(inverted_list) == 1:
                inverted_lists.append((inverted_list[0]['sids'], inverted_list[0]['cardinality']))
        except:
            raise NotImplementedError

    return inverted_lists


def get_strings(sids):
    strings = list()
    for sid in sids:
        try:
            cursor = db.dense_index.find({'_id': sid}, {'string': 1, '_id': 0})
            string_rec = [rec for rec in cursor]
            assert len(string_rec) == 1
            strings.append(string_rec[0]['string'])
        except:
            raise NotImplementedError

    return strings
