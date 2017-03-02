# Copyright 2007-2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

class IndexerCommon(object):
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
