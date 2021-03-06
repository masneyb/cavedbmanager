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


    def test_convert_lat_lon_to_decimal(self):
        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('39.123456'), '39.123456')
        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('-39.123456'), '-39.123456')

        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('39 11 22'),
                               '39.18944444444444')
        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('-39 11 22'),
                               '-39.18944444444444')

        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('39 11 22.4'),
                               '39.18955555555555')
        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('-39 11 22.4'),
                               '-39.18955555555555')

        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('39 11.34567'), '39.1890945')
        self.assertAlmostEqual(cavedb.utils.convert_lat_lon_to_decimal('-39 11.34567'),
                               '-39.1890945')

        self.assertEqual(cavedb.utils.convert_lat_lon_to_decimal(''), None)
        self.assertEqual(cavedb.utils.convert_lat_lon_to_decimal(None), None)

        self.assertRaises(SyntaxError, cavedb.utils.convert_lat_lon_to_decimal, '39.123a')
        self.assertRaises(SyntaxError, cavedb.utils.convert_lat_lon_to_decimal, 'invalid')


    def test_sanitize_filename(self):
        self.assertEqual(cavedb.utils.sanitize_filename('Person1 and Person2.jpg'), \
                                                        'Person1_and_Person2.jpg')
        self.assertEqual(cavedb.utils.sanitize_filename('Person1 & Person2.jpg'), \
                                                        'Person1_and_Person2.jpg')
        self.assertEqual(cavedb.utils.sanitize_filename('This is a test%!!.jpg'), \
                                                        'This_is_a_test.jpg')
        self.assertEqual(cavedb.utils.sanitize_filename('   Filename123    .jpg     '), \
                                                        'Filename123____.jpg')
        self.assertEqual(cavedb.utils.sanitize_filename('../../../etc/Filename123    .jpg     '), \
                                                        '______etcFilename123____.jpg')
        self.assertEqual(cavedb.utils.sanitize_filename(''), '')
        self.assertEqual(cavedb.utils.sanitize_filename(None), '')
        self.assertEqual(cavedb.utils.sanitize_filename('1.Person1 & Person2.jpg'), \
                                                        '1_Person1_and_Person2.jpg')


if __name__ == '__main__':
    unittest.main()
