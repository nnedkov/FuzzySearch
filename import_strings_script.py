##########################################
#   Filename: import_strings_script.py   #
#   Nedko Stefanov Nedkov                #
#   nedko.stefanov.nedkov@gmail.com      #
#   December 2013                        #
##########################################

''' Import strings from external source '''

from db_connector import db



def get_strings_from_ext_source():
    raise NotImplementedError()


if __name__ == '__main__':
    strings = get_strings_from_ext_source()

    string_recs = list()
    not_strings = list()
    for string in strings:
        if isinstance(string, str):
            string_recs.append({'string': string})
        else:
            not_strings.append(string)

    if string_recs:
        db.strings.insert(string_recs)

    if not_strings:
        print 'Not stored data (due to its non-alphanumeric nature): %s' % not_strings
