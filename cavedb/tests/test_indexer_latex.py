# SPDX-License-Identifier: Apache-2.0

import unittest
import cavedb.indexer_latex

class TestIndexerLatex(unittest.TestCase):
    def test_indexer(self):
        terms = ['Great Cave', 'Dry Fork', 'Cheat River', 'Great Cave of Dry Fork of Cheat River', \
                 'Monongahela River',
                 'Laurel and Backbone mountains:Laurel Mountain:Backbone Mountain']
        indexer = cavedb.indexer_latex.IndexerLatex(terms)
        indexed = indexer.generate_index('The stream in the Great Cave of Dry Fork of Cheat ' + \
                                         'River empties out into the Dry Fork, which is a ' + \
                                         'tributuary of the Cheat River.\n' + \
                                         '\n' +
                                         'The Cheat River is a tributuary of the Monongahela ' + \
                                         'River.\n' + \
                                         '\n' + \
                                         'Laurel and Backbone mountains are within the county.\n')
        self.assertEqual(indexed, 'The stream in the \\index{Great Cave of Dry Fork of Cheat ' + \
                                  'River}Great Cave of Dry Fork of Cheat River empties out ' + \
                                  'into the \\index{Dry Fork}Dry Fork, which is a tributuary ' + \
                                  'of the \\index{Cheat River}Cheat River.\n' + \
                                  '\n' + \
                                  'The \\index{Cheat River}Cheat River is a tributuary of the ' + \
                                  '\\index{Monongahela River}Monongahela River.\n' + \
                                  '\n' + \
                                  '\\index{Laurel Mountain}\\index{Backbone Mountain}Laurel ' + \
                                  'and Backbone mountains are within the county.\n')

if __name__ == '__main__':
    unittest.main()
