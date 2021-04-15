# SPDX-License-Identifier: Apache-2.0

import cavedb.indexer_common

class IndexerLatex(cavedb.indexer_common.IndexerCommon):
    def __init__(self, terms):
        cavedb.indexer_common.IndexerCommon.__init__(self, terms)


    def get_index_str(self, search_term, index_terms):
        #pylint: disable=no-self-use

        indexstr = ''
        for index_term in index_terms:
            indexstr = r'%s\index{%s}' % (indexstr, index_term)

        return r'%s%s' % (indexstr, search_term)


    def dump_terms(self, file_handle):
        file_handle.write('\n% Indexed Terms\n')
        for term in self.__sorted_terms:
            digest = self.__term_to_digest[term]
            replacement = self.__digest_to_index[digest]

            file_handle.write('%% %s\t%s\t%s\n' % (term, digest, replacement))
        file_handle.write('\n')
