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
from miscutils import get_qgrams_from_string, time_me, get_string_elements, \
                      ed_property_is_satisfied, strings_are_within_distance_K


def find_approximate_string_matches(qstring):
    in_operation = asme_is_in_operation()
    if not in_operation:
        return None

    candidate_string_ids = get_candidate_string_ids(qstring)
    if not candidate_string_ids:
        return list()

    candidate_strings = get_strings_by_ids(candidate_string_ids)

    candidate_strings_elements = dict()
    for string in candidate_strings:
        candidate_strings_elements[string] = (get_string_elements(string), len(string))

    matching_strings = remove_false_positives(qstring, candidate_strings)
    matching_strings = remove_false_positives(qstring, candidate_strings, candidate_strings_elements)

    return matching_strings


def get_candidate_string_ids(qstring):
    qgrams = get_qgrams_from_string(qstring, QGRAM_LENGTH)
    if not qgrams:
        return list()

    qlength = len(qstring)
    valid_lengths = range(qlength-ED_THRESHOLD, qlength+ED_THRESHOLD+1)
    candidate_string_ids = list()

    for length in valid_lengths:
        string_ids = solve_T_occurence_problem(qlength, length, qgrams)
        if string_ids:
            candidate_string_ids += string_ids

    assert len(candidate_string_ids) == len(set(candidate_string_ids))

    return candidate_string_ids


def solve_T_occurence_problem(qlength, length, qgrams):
    inverted_lists = get_inverted_lists(length, list(set(qgrams)))
    if not inverted_lists:
        return list()

    string_ids = list()

    for inverted_list, _ in inverted_lists:
        string_ids += inverted_list

    qgrams_num = max(length, qlength) - QGRAM_LENGTH + 1
    max_mismatches = QGRAM_LENGTH * ED_THRESHOLD
    duplicates = len(qgrams) - len(set(qgrams))
    T = max(0, qgrams_num - max_mismatches - duplicates)

    if T > 1:
        passing_string_ids = list()

        for string_id, occurrences in groupby(sorted(string_ids)):
            if len(list(occurrences)) >= T:
                passing_string_ids.append(string_id)
    else:
        passing_string_ids = list(set(string_ids))

    return passing_string_ids


@time_me
def remove_false_positives(qstring, candidate_strings, candidate_string_elements=None):
    qlength = len(qstring)

    if candidate_string_elements and len(candidate_strings) > 15:
        qelements = get_string_elements(qstring)
        filtered_candidate_strings = list()

        for string in candidate_strings:
            elements, length = candidate_string_elements[string]
            if ed_property_is_satisfied(qelements, elements, qlength == length):
                filtered_candidate_strings.append(string)

        #print 'Candidate strings before filtering: %s' % len(candidate_strings)
        #print 'Candidate strings after filtering: %s' % len(filtered_candidate_strings)

        candidate_strings = filtered_candidate_strings

    approximate_matches = list()

    for string in candidate_strings:
        is_not_false_positive = strings_are_within_distance_K(qstring, string, qlength, len(string), ED_THRESHOLD+1)

        if is_not_false_positive:
            approximate_matches.append(string)

    return approximate_matches


def verify_results(qstring, approximate_matches):
    qlength = len(qstring)
    valid_lengths = range(qlength-ED_THRESHOLD, qlength+ED_THRESHOLD+1)
    candidate_strings = get_strings_by_lengths(valid_lengths)
    distance_cache = dict()
    verified_approximate_matches = list()

    for string in candidate_strings:
        edit_distance = distance(unicode(qstring), unicode(string))
        distance_cache[unicode(string)] = edit_distance
        if edit_distance < ED_THRESHOLD + 1:
            verified_approximate_matches.append(string)

    missing_matches = [(unicode(i), distance_cache[unicode(i)]) for i in verified_approximate_matches if not i in approximate_matches]
    missed_matches = [(unicode(i), distance_cache[unicode(i)]) for i in approximate_matches if i not in verified_approximate_matches]

    assert not missing_matches, 'Missing matches for %s: %s' % (qstring, missing_matches)
    assert not missed_matches, 'Missed matches for %s: %s' % (qstring, missed_matches)


if __name__ == '__main__':
    if len(argv) == 1:
        strings = get_all_strings()
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
