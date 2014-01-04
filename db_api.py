#######################################
#   Filename: db_api.py               #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Database interface '''

from config import IS_SET

import pymongo
from db_connector import db



# **********   Getters for collection 'strings'   ********** #

def get_all_strings():
    query = {}
    projection = {'string': 1, '_id': 0}

    try:
        cursor = db.strings.find(query, projection)
    except:
        raise NotImplementedError

    strings = [rec['string'] for rec in cursor]

    return strings


# **********   Setters for collection 'strings'   ********** #

def set_strings(strings):
    string_recs = [{'string': string} for string in strings]

    try:
        db.strings.insert(string_recs)
    except:
        raise NotImplementedError


# **********   Getters for collection 'dense_index'   ********** #

def dense_index_is_set():
    query = {'_id': IS_SET}

    try:
        is_set = bool(db.dense_index.find(query).count())
    except:
        raise NotImplementedError

    return is_set


def get_strings_by_ids(sids):
    query = {'_id': {'$in': sids}}
    projection = {'string': 1, '_id': 0}

    try:
        cursor = db.dense_index.find(query, projection)
    except:
        raise NotImplementedError

    strings = [rec['string'] for rec in cursor]

    return strings


def get_strings_by_lengths(lengths):
    query = {'length': {'$in': lengths}}
    projection = {'string': 1, '_id': 0}

    try:
        cursor = db.dense_index.find(query, projection)
    except:
        NotImplementedError

    strings = [rec['string'] for rec in cursor]

    return strings


# **********   Setters for collection 'dense_index'   ********** #

def set_dense_index(dense_index):
    dense_index_recs = [{'_id': sid, 'string': string, 'length': len(string)} \
                                    for sid, string in dense_index.iteritems()]
    dense_index_recs.append({'_id': IS_SET})

    try:
        db.dense_index.drop()
        db.dense_index.insert(dense_index_recs)
        db.dense_index.ensure_index('length', pymongo.ASCENDING)
    except:
        raise NotImplementedError


# **********   Getters for collection 'inverted_index'   ********** #

def inverted_index_is_set():
    query = {'_id': IS_SET}

    try:
        is_set = bool(db.inverted_index.find(query).count())
    except:
        raise NotImplementedError

    return is_set


def get_inverted_lists(length, qgrams):
    query = {'length': length, 'qgram': {'$in': qgrams}}
    projection = {'sids': 1, 'cardinality': 1, '_id': 0}

    try:
        cursor = db.inverted_index.find(query, projection)
    except:
        raise NotImplementedError

    inverted_lists = [(rec['sids'], rec['cardinality']) for rec in cursor]

    return inverted_lists


# **********   Setters for collection 'inverted_index'   ********** #

def set_inverted_index(inverted_index):
    coll_index = [('length', pymongo.ASCENDING), ('qgram', pymongo.ASCENDING)]
    inverted_index_recs = list()

    for length, inverted_index_len in inverted_index.iteritems():
        for qgram, sids in inverted_index_len.iteritems():
            sids = list(sids)
            rec = {'length': length, 'qgram': qgram, \
                   'sids': sids, 'cardinality': len(sids)}
            inverted_index_recs.append(rec)

    inverted_index_recs.append({'_id': IS_SET})

    try:
        db.dense_index.ensure_index(coll_index)
        db.inverted_index.drop()
        db.inverted_index.insert(inverted_index_recs)
    except:
        raise NotImplementedError


# **********   Etc   ********** #

def asme_is_in_operation():
    return dense_index_is_set() and inverted_index_is_set()
