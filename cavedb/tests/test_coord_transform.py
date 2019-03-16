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
from cavedb.coord_transform import TransformedCoordinate

class TestTransformedCoordinate(unittest.TestCase):
    def test_from_utm_nad27(self):
        transformer = TransformedCoordinate('NAD27', 17, 1, 602346, 4388874, None, None)
        self.assertEqual(transformer.get_utm_nad27(),
                         (602346, 4388874))
        self.assert_tuple_almost_equal(transformer.get_utm_nad83(),
                                       (602362.2488997985, 4389092.512418542))
        self.assert_tuple_almost_equal(transformer.get_lon_lat_wgs84(),
                                       (-79.80697562078743, 39.64550098182764))


    def test_from_utm_nad83(self):
        transformer = TransformedCoordinate('NAD83', 17, 1, 602362, 4389092, None, None)
        self.assert_tuple_almost_equal(transformer.get_utm_nad27(),
                                       (602345.751114615, 4388873.487573433))
        self.assertEqual(transformer.get_utm_nad83(),
                         (602362, 4389092))
        self.assert_tuple_almost_equal(transformer.get_lon_lat_wgs84(),
                                       (-79.80697860044248, 39.6454963964772))


    def test_from_lat_lon_wgs84(self):
        transformer = TransformedCoordinate('WGS84', 17, 1, None, None,
                                            -79.80697562078743, 39.64550098182764)
        self.assert_tuple_almost_equal(transformer.get_utm_nad27(),
                                       (602346.0000000328, 4388873.999999977))
        self.assert_tuple_almost_equal(transformer.get_utm_nad83(),
                                       (602362.2489011667, 4389092.512315645))
        self.assert_tuple_almost_equal(transformer.get_lon_lat_wgs84(),
                                       (-79.80697562078743, 39.64550098182764))


    def test_from_lat_lon_wgs84_no_utm(self):
        transformer = TransformedCoordinate('WGS84', None, None, None, None,
                                            -79.80697562078743, 39.64550098182764)
        self.assertEqual(transformer.get_utm_nad27(), (None, None))
        self.assertEqual(transformer.get_utm_nad83(), (None, None))
        self.assert_tuple_almost_equal(transformer.get_lon_lat_wgs84(),
                                       (-79.80697562078743, 39.64550098182764))


    def test_from_none(self):
        transformer = TransformedCoordinate('WGS84', 17, 1, None, None, None, None)
        self.assertEqual(transformer.get_utm_nad27(), (None, None))
        self.assertEqual(transformer.get_utm_nad83(), (None, None))
        self.assertEqual(transformer.get_lon_lat_wgs84(), (None, None))


    def test_from_none2(self):
        transformer = TransformedCoordinate(None, None, None, None, None, None, None)
        self.assertEqual(transformer.get_utm_nad27(), (None, None))
        self.assertEqual(transformer.get_utm_nad83(), (None, None))
        self.assertEqual(transformer.get_lon_lat_wgs84(), (None, None))


    def assert_tuple_almost_equal(self, first, second):
        if len(first) != len(second):
            self.fail('First and second tuples are of different lengths (%d vs %d)' %
                      (len(first), len(second)))

        for first_, second_ in zip(first, second):
            super().assertAlmostEqual(first_, second_, places=5)


if __name__ == '__main__':
    unittest.main()
