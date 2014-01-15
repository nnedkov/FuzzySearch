#######################################
#   Filename: query.py                #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Querying for approximate string matches '''

from config import QGRAM_LENGTH, ED_THRESHOLD, DEBUG_MODE

from itertools import groupby
from time import time
from Levenshtein import distance
from sys import argv

from db_api import asme_is_in_operation, get_inverted_lists, \
                   get_string_attrs_by_ids, get_strings_by_lengths, \
                   get_all_strings
from miscutils import get_qgrams_from_string, get_string_elements, \
                      ed_property_is_satisfied, strings_are_within_distance_K



def find_approximate_string_matches(qstring):
    in_operation = asme_is_in_operation()
    if not in_operation:
        return None

    candidate_string_ids = get_candidate_string_ids(qstring)
    if not candidate_string_ids:
        return list()

    candidate_string_attrs = get_string_attrs_by_ids(candidate_string_ids)
    candidate_strings = candidate_string_attrs.keys()

    matching_strings_wof, twof = remove_false_positives(qstring, candidate_strings)
    matching_strings_wf, twf = remove_false_positives(qstring, candidate_strings, candidate_string_attrs)

    assert matching_strings_wof == matching_strings_wf

    return matching_strings_wf, twof, twf


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


CAND_STRINGS_THRESHOLD = 0

def remove_false_positives(qstring, candidate_strings, candidate_string_attrs=None):
    start_time = int(round(time() * 1000000))

    qlength = len(qstring)

    if candidate_string_attrs and len(candidate_strings) > CAND_STRINGS_THRESHOLD:
        qelements = get_string_elements(qstring)
        filtered_candidate_strings = list()

        for string in candidate_strings:
            elements, length = candidate_string_attrs[string]
            if ed_property_is_satisfied(qelements, elements, qlength == length):
                filtered_candidate_strings.append(string)

        #print '# of candidate strings before filtering: %s' % len(candidate_strings)
        #print '# of candidate strings after filtering: %s' % len(filtered_candidate_strings)

        candidate_strings = filtered_candidate_strings

    approximate_matches = list()

    for string in candidate_strings:
        length = len(string)
        is_not_false_positive = strings_are_within_distance_K(qstring, string, qlength, length, K=ED_THRESHOLD+1)

        if is_not_false_positive:
            approximate_matches.append(string)

    end_time = int(round(time() * 1000000))

    return approximate_matches, end_time - start_time


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

    missing_matches = [(unicode(i), distance_cache[unicode(i)]) for i in verified_approximate_matches if i not in approximate_matches]
    missed_matches = [(unicode(i), distance_cache[unicode(i)]) for i in approximate_matches if i not in verified_approximate_matches]

    assert not missing_matches, 'Missing matches for %s: %s' % (qstring, missing_matches)
    assert not missed_matches, 'Missed matches for %s: %s' % (qstring, missed_matches)


if __name__ == '__main__':
    if len(argv) == 1:
        strings = get_all_strings()[139654:141000]
    else:
        strings = argv[1:]

    strings_num = len(strings)

# **********   EVALUATION   ********** #

    cand_strings_threshold_evaluation = dict()

    for cand_strings_threshold in [5, 15, 25, 35, 45, 55]:
        CAND_STRINGS_THRESHOLD = cand_strings_threshold
        cand_strings_threshold_evaluation[cand_strings_threshold] = dict()

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

            approximate_matches, twof, twf = find_approximate_string_matches(query_string)
            print approximate_matches
            qlength = len(query_string)
            try:
                cand_strings_threshold_evaluation[cand_strings_threshold][qlength][0] += 1
                cand_strings_threshold_evaluation[cand_strings_threshold][qlength][1] += twof
                cand_strings_threshold_evaluation[cand_strings_threshold][qlength][2] += twf
            except KeyError:
                cand_strings_threshold_evaluation[cand_strings_threshold][qlength] = [1, twof, twf]

            if DEBUG_MODE:
                verify_results(query_string, approximate_matches)

    for cand_strings_threshold, evaluation in cand_strings_threshold_evaluation.iteritems():
        print '\n\nCANDIDATE STRINGS THRESHOLD: %s\n' % cand_strings_threshold

        for qlength, attr in evaluation.iteritems():
            print 'Qstring length: %s - Count: %s - Average time without filtering: %s - Average time with filtering: %s' % (qlength, attr[0], attr[1]/attr[0], attr[2]/attr[0])

# **********   EVALUATION   ********** #
