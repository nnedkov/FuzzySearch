#######################################
#   Filename: indexer.py              #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

""" String indexer """

from Queue import Queue
from threading import Thread
from dbapi import get_all_strings, set_dense_index



def index_strings():
    strings = get_all_strings()

    if not strings:
        raise Exception('No strings to index')

    # Threading is used because it reduces indexing time to half.
    threads = list()

    # If an exception/error occurs in any of the threads it is
    # not detectable, hence inter-thread communication is used.
    queue = Queue()

    threads.append(Thread(target=create_inverted_lists, args=(strings, queue)))
    threads.append(Thread(target=create_dense_index, args=(strings, queue)))

    for t in threads:
        t.start()

    for t in threads:
        all_ok, error = queue.get(block=True)
        if not all_ok:
            raise error
        queue.task_done()

    for t in threads:
        t.join()


def create_inverted_lists(strings, queue):

    def _create_inverted_lists(strings):
        raise NotImplementedError('Well the error says it all!')


    result = (True, None)

    try:
        _create_inverted_lists(strings)
    except Exception as e:
        result = (False, e)

    queue.put(result)


def create_dense_index(strings, queue):

    def _create_dense_index(strings):
        string_id = 0
        dense_index = dict()
        for string in strings:
            dense_index[string_id] = string
            string_id += 1

        set_dense_index(dense_index)


    result = (True, None)

    try:
        _create_dense_index(strings)
    except Exception as e:
        result = (False, e)

    queue.put(result)
