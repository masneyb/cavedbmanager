# SPDX-License-Identifier: Apache-2.0

# A not so efficient indexer. This class takes as input a list of strings
# that will be indexed. At a high level:
#
# - Take the input string, and go through the list of indexed terms, from
#   longest to shortest, and replace each occurance with the sha256 digest of
#   the message term.
# - Once this has been done, go through all of the sha256 digests, and replace
#   each occurance with the proper latex \index{} code.
#
# See tests/test_latex_indexer.py for an example.

import hashlib

class IndexerCommon():
    def __init__(self, terms):
        self.__sorted_terms = []
        self.__term_to_digest = {}
        self.__digest_to_index = {}

        for term in terms:
            all_index_terms = term.split(':')
            if len(all_index_terms) == 1:
                self.__add_term(term, [term])
            else:
                self.__add_term(all_index_terms[0], all_index_terms[1:])

        self.__sorted_terms.sort(key=len, reverse=True)


    def get_index_str(self, search_term, index_terms):
        #pylint: disable=no-self-use,unused-argument
        return search_term


    def __add_term(self, search_term, index_terms):
        self.__sorted_terms.append(search_term)

        search_term_digest = hashlib.sha256(search_term.encode('UTF-8')).hexdigest()
        self.__term_to_digest[search_term] = search_term_digest
        self.__digest_to_index[search_term_digest] = self.get_index_str(search_term, index_terms)


    def generate_index(self, inputstr):
        for term in self.__sorted_terms:
            digest = self.__term_to_digest[term]

            # This appears to be quicker than doing a single regular expression
            for suffix in [' ', '.', ',', ':', ')', '\'']:
                inputstr = inputstr.replace('%s%s' % (term, suffix),
                                            '%s%s' % (digest, suffix))

        for digest, replacement in list(self.__digest_to_index.items()):
            inputstr = inputstr.replace(digest, replacement)

        return inputstr
