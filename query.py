#######################################
#   Filename: indexer.py              #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Approximate string matching '''

from config import QGRAM_LEN, ED_THRESHOLD, MATCHING_QGRAMS_PERCENTAGE

from sys import argv
from operator import itemgetter
from db_api import asme_is_in_operation, get_inverted_lists, get_strings
from miscutils import get_qgrams_from_string



def find_approximate_strings(qstring):
    in_operation = asme_is_in_operation()
    if not in_operation:
        return None

    candidate_sids = get_candidate_string_ids(qstring)
    if not candidate_sids:
        return list()

    candidate_strings = get_strings(candidate_sids)
    matching_strings = remove_false_positives(candidate_strings)

    return matching_strings


def get_candidate_string_ids(qstring):
    qgrams = set(get_qgrams_from_string(qstring, QGRAM_LEN))
    if not qgrams:
        return list()

    candidate_strings = set()
    qstring_length = len(qstring)
    valid_lengths = range(qstring_length-ED_THRESHOLD, qstring_length+ED_THRESHOLD)
    for length in valid_lengths:
        string_ids = solve_T_occurence_problem(length, qgrams)
        if string_ids:
            candidate_strings |= string_ids

    return candidate_strings


def solve_T_occurence_problem(length, qgrams):
    inverted_lists = get_inverted_lists(length, qgrams)
    if not inverted_lists:
        return set()

    inverted_lists = sorted(inverted_lists, key=itemgetter(1), reverse=True)

    T = int(MATCHING_QGRAMS_PERCENTAGE * len(inverted_lists))
    string_ids = set(inverted_lists[0][0])

    for i in range(1, T):
        inverted_list = set(inverted_lists[i][0])
        string_ids &= inverted_list

    return string_ids

def remove_false_positives(candidate_strings):
    return candidate_strings


if __name__ == '__main__':
    approximate_strings = find_approximate_strings(argv[1])
    for string in approximate_strings:
        print string

