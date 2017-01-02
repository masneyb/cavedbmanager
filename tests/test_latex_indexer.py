# Copyright 2017 Brian Masney <masneyb@onstation.org>
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

import unittest
import cavedb.latex_indexer

class TestLatexIndexer(unittest.TestCase):
    def test_indexer(self):
        terms = ['Great Cave', 'Dry Fork', 'Cheat River', 'Great Cave of Dry Fork of Cheat River', \
                 'Monongahela River',
                 'Laurel and Backbone mountains:Laurel Mountain:Backbone Mountain']
        indexer = cavedb.latex_indexer.LatexIndexer(terms)
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
