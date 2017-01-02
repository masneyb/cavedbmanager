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
#   longest to shortest, and replace each occurance with the MD5 digest of
#   the message term.
# - Once this has been done, go through all of the MD5 digests, and replace
#   each occurance with the proper latex \index{} code.
#
# See tests/test_latex_indexer.py for an example.

import cavedb.indexer_common

class IndexerLatex(cavedb.indexer_common.IndexerCommon):
    def __init__(self, terms):
        cavedb.indexer_common.IndexerCommon.__init__(self, terms)


    def wrap_term(self, index_term):
        #pylint: disable=no-self-use
        return r'\index{%s}' % (index_term)


    def dump_terms(self, file_handle):
        file_handle.write('\n% Indexed Terms\n')
        for term in self.__sorted_terms:
            digest = self.__term_to_digest[term]
            replacement = self.__digest_to_index[digest]

            file_handle.write('%% %s\t%s\t%s\n' % (term, digest, replacement))
        file_handle.write('\n')

