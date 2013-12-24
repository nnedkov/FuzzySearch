#######################################
#   Filename: miscutils.py            #
#   Nedko Stefanov Nedkov             #
#   nedko.stefanov.nedkov@gmail.com   #
#   December 2013                     #
#######################################

''' Miscellaneous utilities '''

def get_qgrams_from_string(string, q):
    qgrams = list()

    for i in range(len(string)+1-q):
        qgrams.append(string[i:i+q])

    return qgrams
