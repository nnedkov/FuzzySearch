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
                      ed_property_is_satisfied, get_pos_qgrams_from_string, \
                      strings_are_within_distance_K



def find_approximate_string_matches(qstring):
    in_operation = asme_is_in_operation()
    if not in_operation:
        return None

    candidate_string_ids = get_candidate_string_ids(qstring)
    if not candidate_string_ids:
        return list()

    candidate_string_attrs = get_string_attrs_by_ids(candidate_string_ids)
    candidate_strings = candidate_string_attrs.keys()

    evaluation = dict()
    evaluation['initial_candidates_num'] = len(candidate_strings)

    start_time = int(round(time() * 1000000))
    filtered_candidate_strings = my_filter(qstring, candidate_strings, candidate_string_attrs)
    filter_time = int(round(time() * 1000000))
    matching_strings1 = remove_false_positives(qstring, filtered_candidate_strings)
    total_time = int(round(time() * 1000000))
    evaluation['my_filter_time'] = filter_time - start_time
    evaluation['my_filter_total_time'] = total_time - start_time
    evaluation['my_filter_pruned'] = len(candidate_strings) - len(filtered_candidate_strings)
    # verify_results(qstring, matching_strings1)

    start_time = int(round(time() * 1000000))
    filtered_candidate_strings = position_filter(qstring, candidate_strings, candidate_string_attrs)
    filter_time = int(round(time() * 1000000))
    matching_strings2 = remove_false_positives(qstring, filtered_candidate_strings)
    total_time = int(round(time() * 1000000))
    evaluation['position_filter_time'] = filter_time - start_time
    evaluation['position_filter_total_time'] = total_time - start_time
    evaluation['position_filter_pruned'] = len(candidate_strings) - len(filtered_candidate_strings)
    # verify_results(qstring, matching_strings2)

    assert matching_strings1 == matching_strings2

    # evaluation['approximate_matches'] = matching_strings1

    return evaluation


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

    T = get_min_matching_qgram_num(query_string, qlength, qgrams)

    if T > 1:
        passing_string_ids = list()

        for string_id, occurrences in groupby(sorted(string_ids)):
            if len(list(occurrences)) >= T:
                passing_string_ids.append(string_id)
    else:
        passing_string_ids = list(set(string_ids))

    return passing_string_ids


CAND_STRINGS_THRESHOLD = 0


def get_min_matching_qgram_num(query_string, qlength=None, qgrams=None):
    if qlength is None:
        qlength = len(query_string)
    if qgrams is None:
        qgrams = get_qgrams_from_string(query_string, QGRAM_LENGTH)

    qgrams_num = qlength - QGRAM_LENGTH + 1   # or max(length, qlength) - QGRAM_LENGTH + 1
    max_mismatches = QGRAM_LENGTH * ED_THRESHOLD
    duplicates = len(qgrams) - len(set(qgrams))
    T = max(0, qgrams_num - duplicates - max_mismatches)

    return T

def my_filter(qstring, candidate_strings, candidate_string_attrs):
    filtered_candidate_strings = candidate_strings

    if len(candidate_strings) > CAND_STRINGS_THRESHOLD:
        qelements = get_string_elements(qstring)
        qlength = len(qstring)
        filtered_candidate_strings = list()

        for string in candidate_strings:
            elements, length, _ = candidate_string_attrs[string]
            if ed_property_is_satisfied(qelements, elements, qlength == length):
                filtered_candidate_strings.append(string)

        print '(my_filter) # of candidate strings before filtering: %s' % len(candidate_strings)
        print '(my_filter) # of candidate strings after filtering: %s' % len(filtered_candidate_strings)

    return filtered_candidate_strings


def position_filter(qstring, candidate_strings, candidate_string_attrs):
    filtered_candidate_strings = candidate_strings

    if len(candidate_strings) > CAND_STRINGS_THRESHOLD:
        query_pos_qgrams = get_pos_qgrams_from_string(qstring, QGRAM_LENGTH)
        filtered_candidate_strings = list()

        for string in candidate_strings:
            _, _, pos_qgrams = candidate_string_attrs[string]
            pos_qgram_matches_numb = 0
            T = max(len(qstring), len(string)) - QGRAM_LENGTH*ED_THRESHOLD - 1
            will_be_pruned = True

            for qgram, query_positions in query_pos_qgrams.iteritems():
                assert query_positions == sorted(query_positions)
                try:
                    positions = list(pos_qgrams[qgram])
                except KeyError:
                    continue

                assert positions == sorted(positions)

                for qpos in query_positions:

                    for pos in positions:
                        if abs(qpos-pos) <= ED_THRESHOLD:
                            positions.remove(pos)
                            pos_qgram_matches_numb += 1
                            break

                    if pos_qgram_matches_numb == T:
                        will_be_pruned = False
                        break

                if not will_be_pruned:
                    break

            if not will_be_pruned:
                filtered_candidate_strings.append(string)

        print '(pos_filter) # of candidate strings before filtering: %s' % len(candidate_strings)
        print '(pos_filter) # of candidate strings after filtering: %s' % len(filtered_candidate_strings)

    return filtered_candidate_strings


def remove_false_positives(qstring, candidate_strings):
    qlength = len(qstring)
    approximate_matches = list()

    for string in candidate_strings:
        length = len(string)
        is_not_false_positive = strings_are_within_distance_K(qstring, string, qlength, length, K=ED_THRESHOLD+1)

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

    missing_matches = [(unicode(i), distance_cache[unicode(i)]) for i in verified_approximate_matches if i not in approximate_matches]
    missed_matches = [(unicode(i), distance_cache[unicode(i)]) for i in approximate_matches if i not in verified_approximate_matches]

    assert not missing_matches, 'Missing matches for %s: %s' % (qstring, missing_matches)
    assert not missed_matches, 'Missed matches for %s: %s' % (qstring, missed_matches)


if __name__ == '__main__':
#    if len(argv) == 1:
#        strings = get_strings_by_lengths([6])[:500]
#        strings += get_strings_by_lengths([7])[:500]
#        strings += get_strings_by_lengths([8])[:500]
#        strings += get_strings_by_lengths([9])[:500]
#        strings += get_strings_by_lengths([10])[:500]
#        strings += get_strings_by_lengths([11])[:500]
#        # strings = get_all_strings()[139654:141000]
#    else:
#        strings = argv[1:]
#
#    strings_num = len(strings)

# **********   EVALUATION   ********** #
    SAMPLE_SIZE = 100

    for CAND_STRINGS_THRESHOLD in [25, 35, 45, 55, 5, 15]:

        for qlength in [6, 7, 8, 9, 10]:
            strings = get_strings_by_lengths([qlength])
            evaluation = [0] * 7
            current_sample = 0

            for query_string in strings:
                try:
                    unicode(query_string)
                except UnicodeDecodeError:
                    print '%s/%s: %s (skip because of encoding issues)' % (current_sample, SAMPLE_SIZE, query_string)
                    continue

                if len(query_string) <= QGRAM_LENGTH + 1:
                    print '%s/%s: %s (skip because of its small length)' % (current_sample, SAMPLE_SIZE, query_string)
                    continue

                if get_min_matching_qgram_num(query_string, qlength) == 0:
                    print '%s/%s: %s (skip because T is 0)' % (current_sample, SAMPLE_SIZE, query_string)
                    continue

                print '%s/%s: %s' % (current_sample, SAMPLE_SIZE, query_string)

                qs_evaluation = find_approximate_string_matches(query_string)
                if qs_evaluation['initial_candidates_num'] <= CAND_STRINGS_THRESHOLD:
                    continue

                current_sample += 1
                evaluation[0] += qs_evaluation['initial_candidates_num']
                evaluation[1] += qs_evaluation['my_filter_pruned']
                evaluation[2] += qs_evaluation['position_filter_pruned']
                evaluation[3] += qs_evaluation['my_filter_total_time']
                evaluation[4] += qs_evaluation['position_filter_total_time']
                evaluation[5] += qs_evaluation['my_filter_time']
                evaluation[6] += qs_evaluation['position_filter_time']

                # if DEBUG_MODE:
                #     verify_results(query_string, qs_evaluation['approximate_matches'])

                if current_sample == SAMPLE_SIZE:
                    out_string = 'CAND_STRINGS_THRESHOLD: %s\n' % CAND_STRINGS_THRESHOLD
                    out_string += 'Query string length: %s\n' % qlength
                    out_string += 'Count: %s\n' % SAMPLE_SIZE
                    out_string += 'Percentage of pruned candidates (my filter): %d%%\n' % (evaluation[1]*100/evaluation[0])
                    out_string += 'Percentage of pruned candidates (pos filter): %d%%\n' % (evaluation[2]*100/evaluation[0])
                    avg_total_time_my_filter = evaluation[3]/SAMPLE_SIZE
                    avg_total_time_pos_filter = evaluation[4]/SAMPLE_SIZE
                    avg_total_boost = 100 - (100*avg_total_time_my_filter/avg_total_time_pos_filter)
                    out_string += 'Average total boost (my filter): %d%%\n' % avg_total_boost
                    avg_time_my_filter = evaluation[5]/SAMPLE_SIZE
                    avg_time_pos_filter = evaluation[6]/SAMPLE_SIZE
                    avg_filter_boost = 100 - (100*avg_time_my_filter/avg_time_pos_filter)
                    out_string += 'Average filter boost (my filter): %d%%\n' % avg_filter_boost
                    out_string += '\n\n\n'

                    with open('output.txt', 'a') as outf:
                        outf.write(out_string)

                    break


# **********   EVALUATION   ********** #
