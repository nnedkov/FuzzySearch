############################################
#   Filename: output_length_frequency.py   #
#   Nedko Stefanov Nedkov                  #
#   nedko.stefanov.nedkov@gmail.com        #
#   February 2014                          #
############################################

''' Output length frequency for string collections '''

from operator import itemgetter

from db_connector import db



def get_strings_from_collection(collection):
    query = {}
    projection = {'string': 1, '_id': 0}

    cursor = collection.find(query, projection)
    strings = [rec['string'] for rec in cursor]

    return strings


if __name__ == '__main__':
    collections = [(db.english_words, 'english_words'), \
                   (db.inspire_authors, 'inspire_authors'), \
                   (db.imdb_actors_directors, 'imdb_actors_directors')]

    for collection, coll_name in collections:
        strings = get_strings_from_collection(collection)
        length_frequency = dict()

        for string in strings:
            string_len = len(string)
            try:
                length_frequency[string_len] += 1
            except KeyError:
                length_frequency[string_len] = 1

        length_frequency = [(length, count) for length, count in length_frequency.iteritems()]
        length_frequency = sorted(length_frequency, key=itemgetter(0))

        out_string = ''
        for length, count in length_frequency:
            out_string += '%s\t%s\n' % (length, count)

        out_file = './plots/%s/length_frequency/length_frequency.txt' % coll_name
        with open(out_file, 'w') as fp:
            fp.write(out_string)

        print '\nCollection: %s, size: %s' % (coll_name, len(strings))
        for length, count in length_frequency:
            print 'Length: %s, count: %s' % (length, count)
