# Copyright 2007-2016 Brian Masney <masneyb@onstation.org>
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
import cavedb.utils

class TestUtils(unittest.TestCase):
    def test_get_normalized_date(self):
        self.assertEqual(cavedb.utils.get_normalized_date('Sep 1997'), '1997-09-01')
        self.assertEqual(cavedb.utils.get_normalized_date('Sep 21, 1997'), '1997-09-21')
        self.assertEqual(cavedb.utils.get_normalized_date('Fall 1997'), '1997-10-01')
        self.assertEqual(cavedb.utils.get_normalized_date('Fall/Winter 1997'), '1997-10-01')

if __name__ == '__main__':
    unittest.main()