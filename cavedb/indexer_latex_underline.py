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
