# SPDX-License-Identifier: Apache-2.0

import cavedb.indexer_latex

class IndexerLatexUnderline(cavedb.indexer_latex.IndexerLatex):
    def __init__(self, terms):
        cavedb.indexer_latex.IndexerLatex.__init__(self, terms)


    def get_index_str(self, search_term, index_terms):
        #pylint: disable=no-self-use

        indexstr = ''
        for index_term in index_terms:
            indexstr = r'%s\index{%s}' % (indexstr, index_term)

        return r'%s\underline{%s}' % (indexstr, search_term)
