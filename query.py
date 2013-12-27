#######################################
#   Filename: query.py                #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Querying for approximate string matches '''

from config import QGRAM_LENGTH, ED_THRESHOLD

from itertools import groupby
from Levenshtein import distance
from sys import argv

from db_api import asme_is_in_operation, get_inverted_lists, \
                   get_strings_by_ids, get_strings_by_lengths, get_all_strings
from miscutils import get_qgrams_from_string



def find_approximate_string_matches(qstring):
    in_operation = asme_is_in_operation()
    if not in_operation:
        return None

    candidate_string_ids = get_candidate_string_ids(qstring)
    if not candidate_string_ids:
        return list()

    candidate_strings = get_strings_by_ids(candidate_string_ids)
    matching_strings = remove_false_positives(qstring, candidate_strings)

    return matching_strings


def get_candidate_string_ids(qstring):
    qgrams = get_qgrams_from_string(qstring, QGRAM_LENGTH)
    if not qgrams:
        return list()

    qstring_length = len(qstring)
    valid_lengths = range(qstring_length-ED_THRESHOLD, qstring_length+ED_THRESHOLD+1)
    candidate_string_ids = list()

    for length in valid_lengths:
        string_ids = solve_T_occurence_problem(length, qgrams, qstring_length)
        if string_ids:
            candidate_string_ids += string_ids

    assert len(candidate_string_ids) == len(set(candidate_string_ids))

    return candidate_string_ids


def solve_T_occurence_problem(length, qgrams, qstring_len):
    inverted_lists = get_inverted_lists(length, list(set(qgrams)))
    if not inverted_lists:
        return list()

    string_ids = list()

    for inverted_list, _ in inverted_lists:
        string_ids += inverted_list

    duplicate_qgrams = len(qgrams)-len(set(qgrams))
    valid_qgram_mismatches_num = QGRAM_LENGTH * ED_THRESHOLD
    T = max(0, qstring_len - QGRAM_LENGTH + 1 - valid_qgram_mismatches_num - duplicate_qgrams)

    if T > 1:
        passing_string_ids = list()

        for string_id, occurrences in groupby(sorted(string_ids)):
            if len(list(occurrences)) >= T:
                passing_string_ids.append(string_id)
    else:
        passing_string_ids = list(set(string_ids))

    return passing_string_ids


def remove_false_positives(qstring, candidate_strings):
    approximate_matches = list()

    for string in candidate_strings:

        if distance(unicode(qstring), unicode(string)) <= ED_THRESHOLD:
            approximate_matches.append(string)

    return approximate_matches


def verify_results(qstring, approximate_matches):
    qstring_len = len(qstring)
    valid_lengths = range(qstring_len-ED_THRESHOLD, qstring_len+ED_THRESHOLD+1)
    candidate_strings = get_strings_by_lengths(valid_lengths)
    distance_cache = dict()
    verified_approximate_matches = list()

    for string in candidate_strings:
        edit_distance = distance(unicode(qstring), unicode(string))
        distance_cache[unicode(string)] = edit_distance
        if edit_distance <= ED_THRESHOLD:
            verified_approximate_matches.append(string)

    missing_matches = [(unicode(i), distance_cache[unicode(i)]) for i in verified_approximate_matches if not i in approximate_matches]
    missed_matches = [(unicode(i), distance_cache[unicode(i)]) for i in approximate_matches if i not in verified_approximate_matches]

    assert not missing_matches, 'Missing matches for %s: %s' % (qstring, missing_matches)
    assert not missed_matches, 'Missed matches for %s: %s' % (qstring, missed_matches)


if __name__ == '__main__':
    if len(argv) == 1:
        strings = get_all_strings()[669:]
    else:
        strings = argv[1:]

    strings_num = len(strings)

    for i, query_string in enumerate(strings):
        try:
            unicode(query_string)
        except UnicodeDecodeError:
            print '%s/%s: %s (skip because of encoding issues)' % (i+1, strings_num, query_string)
            continue

        if len(query_string) <= QGRAM_LENGTH + 1:
            print '%s/%s: %s (skip because of its small length)' % (i+1, strings_num, query_string)
            continue

        print '%s/%s: %s' % (i+1, strings_num, query_string)

        approximate_matches = find_approximate_string_matches(query_string)
        verify_results(query_string, approximate_matches)
