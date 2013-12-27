#######################################
#   Filename: db_api.py               #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Database interface '''

from config import IS_SET

from db_connector import db
import pymongo



# **********   Getters for collection 'strings'   ********** #

def get_all_strings():
    try:
        cursor = db.strings.find({}, {'string': 1, '_id': 0})
    except:
        raise NotImplementedError

    strings = [rec['string'] for rec in cursor]

    return strings


# **********   Getters for collection 'dense_index'   ********** #

def dense_index_is_set():
    try:
        is_set = bool(db.dense_index.find({'_id': IS_SET}).count())
    except:
        raise NotImplementedError

    return is_set


def get_strings_by_ids(sids):
    strings = list()

    try:
        cursor = db.dense_index.find({'_id': {'$in': sids}}, {'string': 1, '_id': 0})
    except:
        raise NotImplementedError

    strings = [rec['string'] for rec in cursor]

    return strings


def get_strings_by_lengths(lengths):
    strings = list()

    try:
        cursor = db.dense_index.find({'length': {'$in': lengths}}, {'string': 1, '_id': 0})
    except:
        NotImplementedError

    strings = [rec['string'] for rec in cursor]

    return strings


# **********   Setters for collection 'dense_index'   ********** #

def set_dense_index(dense_index):
    dense_index_recs = [{'_id': sid, 'string': string, 'length': len(string)} for sid, string in dense_index.iteritems()]
    dense_index_recs.append({'_id': IS_SET})

    try:
        db.dense_index.drop()
        db.dense_index.insert(dense_index_recs)
        db.dense_index.ensure_index('length', pymongo.ASCENDING)
    except:
        raise NotImplementedError


# **********   Getters for collection 'inverted_index'   ********** #

def inverted_index_is_set():
    try:
        is_set = bool(db.inverted_index.find({'_id': IS_SET}).count())
    except:
        raise NotImplementedError

    return is_set


def get_inverted_lists(length, qgrams):
    try:
        cursor = db.inverted_index.find({'length': length, 'qgram': {'$in': qgrams}}, {'sids': 1, 'cardinality': 1, '_id': 0})
    except:
        raise NotImplementedError

    inverted_lists = [(rec['sids'], rec['cardinality']) for rec in cursor]

    return inverted_lists


# **********   Setters for collection 'inverted_index'   ********** #

def set_inverted_index(inverted_index):
    inverted_index_recs = list()

    for length, inverted_index_len in inverted_index.iteritems():
        for qgram, sids in inverted_index_len.iteritems():
            sids = list(sids)
            inverted_index_recs.append({'length': length, 'qgram': qgram, 'sids': sids, 'cardinality': len(sids)})

    inverted_index_recs.append({'_id': IS_SET})

    try:
        db.inverted_index.drop()
        db.inverted_index.insert(inverted_index_recs)
    except:
        raise NotImplementedError


# **********   Etc   ********** #

def asme_is_in_operation():
    return dense_index_is_set() and inverted_index_is_set()
