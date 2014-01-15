#######################################
#   Filename: db_api.py               #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Database interface '''

from config import IS_SET

from pymongo import errors, ASCENDING
from sys import exc_info
from time import sleep

from db_connector import db



# **********   Getters for collection 'strings'   ********** #

def get_all_strings():
    query = {}
    projection = {'string': 1, '_id': 0}

    cursor = db.strings.find(query, projection)
    strings = [rec['string'] for rec in cursor]

    return strings


# **********   Setters for collection 'strings'   ********** #

def set_strings(strings):
    string_recs = [{'string': string} for string in strings]

    # Handling network failover
    for retries in range(0, 3):
        try:
            db.strings.insert(string_recs)
        except errors.DuplicateKeyError:
            break
        except:
            print exc_info()[0]
            sleep(5)


# **********   Getters for collection 'dense_index'   ********** #

def dense_index_is_set():
    query = {'_id': IS_SET}

    is_set = bool(db.dense_index.find(query).count())

    return is_set


def get_string_attrs_by_ids(sids):
    query = {'_id': {'$in': sids}}
    projection = {'string': 1, 'elements': 1, 'length': 1, '_id': 0}

    cursor = db.dense_index.find(query, projection)
    string_attrs = dict((rec['string'], (rec['elements'], rec['length'])) \
                                                            for rec in cursor)
    return string_attrs


def get_strings_by_lengths(lengths):
    query = {'length': {'$in': lengths}}
    projection = {'string': 1, '_id': 0}

    cursor = db.dense_index.find(query, projection)
    strings = [rec['string'] for rec in cursor]

    return strings


# **********   Setters for collection 'dense_index'   ********** #

def set_dense_index(dense_index):
    dense_index_recs = list()

    for sid, string_attr in dense_index.iteritems():
        string_rec = {'_id': sid,
                      'string': string_attr[0],
                      'elements': string_attr[1],
                      'length': string_attr[2]}
        dense_index_recs.append(string_rec)

    dense_index_recs.append({'_id': IS_SET})

    # Handling network failover
    for retries in range(0, 3):
        try:
            db.dense_index.drop()
            db.dense_index.insert(dense_index_recs)
            db.dense_index.ensure_index('length', ASCENDING)
        except errors.DuplicateKeyError:
            break
        except:
            print exc_info()[0]
            sleep(5)


# **********   Getters for collection 'inverted_index'   ********** #

def inverted_index_is_set():
    query = {'_id': IS_SET}

    is_set = bool(db.inverted_index.find(query).count())

    return is_set


def get_inverted_lists(length, qgrams):
    query = {'length': length, 'qgram': {'$in': qgrams}}
    projection = {'sids': 1, 'cardinality': 1, '_id': 0}

    cursor = db.inverted_index.find(query, projection)
    inverted_lists = [(rec['sids'], rec['cardinality']) for rec in cursor]

    return inverted_lists


# **********   Setters for collection 'inverted_index'   ********** #

def set_inverted_index(inverted_index):
    coll_index = [('length', ASCENDING), ('qgram', ASCENDING)]
    inverted_index_recs = list()

    for length, inverted_index_len in inverted_index.iteritems():
        for qgram, sids in inverted_index_len.iteritems():
            sids = list(sids)
            rec = {'length': length, 'qgram': qgram, \
                   'sids': sids, 'cardinality': len(sids)}
            inverted_index_recs.append(rec)

    inverted_index_recs.append({'_id': IS_SET})

    # Handling network failover
    for retries in range(0, 3):
        try:
            db.inverted_index.drop()
            db.inverted_index.ensure_index(coll_index)
            db.inverted_index.insert(inverted_index_recs)
        except errors.DuplicateKeyError:
            break
        except:
            print exc_info()[0]
            sleep(5)


# **********   Etc   ********** #

def asme_is_in_operation():
    return dense_index_is_set() and inverted_index_is_set()
