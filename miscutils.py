#######################################
#   Filename: miscutils.py            #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Miscellaneous utilities '''

from config import ED_THRESHOLD

from itertools import groupby
from time import time


def get_qgrams_from_string(string, q):
    qgrams = list()

    for i in range(len(string)+1-q):
        qgrams.append(string[i:i+q])

    return qgrams


def get_string_elements(string):
    elements = dict()

    for char, occurences in [(i, len(list(j))) for i, j in groupby(''.join(sorted(list(string))))]:
        elements[char] = occurences

    return elements


def ed_property_is_satisfied(qelements, elements, have_same_length):
    S = R = 0

    for char, qoccurences in qelements.iteritems():
        try:
            occurences = elements[char]
            if qoccurences > occurences:
                S += qoccurences - occurences
        except KeyError:
            S += qoccurences

        if have_same_length and S > ED_THRESHOLD:
            return False

    if have_same_length:
        if S > ED_THRESHOLD:
            return False

        return True

    for char, occurences in elements.iteritems():
        try:
            qoccurences = qelements[char]
            if occurences > qoccurences:
                R += occurences - qoccurences
        except KeyError:
            R += occurences

    if min(R, S) + abs(S-R) > ED_THRESHOLD:
        return False

    return True


def strings_are_within_distance_K(qstring, string, qlength, length, K):
    matrix = [[0 if abs(i-j) < K else K for i in xrange(qlength+1)] for j in xrange(length+1)]
    matrix[0] = range(qlength+1)
    for i in xrange(1, length+1):
        matrix[i][0] = i

    for i in xrange(1, length+1):
        for j in xrange(1, qlength+1):
            if abs(i-j) < K:
                if i == j and min(matrix[i-1][j], matrix[i][j-1], matrix[i][j]) >= K:
                    return False

                if string[i-1] == qstring[j-1]:
                    matrix[i][j] = min(matrix[i-1][j] + 1, matrix[i][j-1] + 1, matrix[i-1][j-1])
                else:
                    matrix[i][j] = min(matrix[i-1][j] + 1, matrix[i][j-1] + 1, matrix[i-1][j-1] + 1)

    if matrix[length][qlength] < K:
        return True

    return False


def time_me(method):
    def wrapper(*args, **kw):
        start_time = int(round(time() * 1000))
        result = method(*args, **kw)
        end_time = int(round(time() * 1000))

        print '%s ms' % (end_time - start_time)

        return result

    return wrapper
