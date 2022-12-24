# SPDX-License-Identifier: Apache-2.0

import osgeo.osr

LAT_LON_WGS84 = osgeo.osr.SpatialReference()
LAT_LON_WGS84.SetWellKnownGeogCS('WGS84')

class TransformedCoordinate():
    def __init__(self, src_datum, utm_zone, is_utm_zone_north, utm_easting, utm_northing, \
                 longitude, latitude):
        # pylint: disable=too-many-arguments

        if src_datum:
            self.in_srs = osgeo.osr.SpatialReference()
            self.in_srs.SetWellKnownGeogCS(src_datum)
        else:
            self.in_srs = None

        if utm_zone is not None and is_utm_zone_north is not None and utm_easting is not None and \
             utm_northing is not None:
            self.in_srs.SetUTM(utm_zone, is_utm_zone_north)
            self.in_xy = (int(utm_easting), int(utm_northing))
        elif longitude is not None and latitude is not None:
            # With the upgrade from gdal 2.2.3 to 3.4.1, previously I would pass in
            # (latitude, longitude). Now it needs to be switched here. The UTM input is still
            # (easting, northing). We also need to swap the output below.
            self.in_xy = (float(latitude), float(longitude))
        else:
            self.in_xy = (None, None)

        if utm_zone is not None and is_utm_zone_north is not None:
            self.utm_nad83 = osgeo.osr.SpatialReference()
            self.utm_nad83.SetUTM(utm_zone, is_utm_zone_north)
            self.utm_nad83.SetWellKnownGeogCS('NAD83')
        else:
            self.utm_nad83 = None

        self.transform_cache = {}

        # Add the original coordinate to the cache to improve the overall processing
        # speed and to ensure that the original coordinate remains unchanged.
        cache_key = (str(self.in_srs), str(self.in_srs), self.in_xy[0], self.in_xy[1])
        self.transform_cache[cache_key] = (self.in_xy[0], self.in_xy[1])


    def transform(self, out_srs):
        if not self.in_srs or not out_srs or not self.in_xy[0] or not self.in_xy[1]:
            return (None, None)

        cache_key = (str(self.in_srs), str(out_srs), self.in_xy[0], self.in_xy[1])
        if cache_key in self.transform_cache:
            return self.transform_cache[cache_key]

        transformer = osgeo.osr.CoordinateTransformation(self.in_srs, out_srs)
        (newx, newy, _) = transformer.TransformPoint(self.in_xy[0], self.in_xy[1])
        ret = (newx, newy)
        self.transform_cache[cache_key] = ret

        return ret


    def get_lon_lat_wgs84(self):
        (newx, newy) = self.transform(LAT_LON_WGS84)
        # With the upgrade from gdal 2.2.3 to 3.4.1, previously it would return
        # (longitude, latitude). Now it needs to be switched here. The UTM input is still
        # returned as (easting, northing).
        return (newy, newx)


    def get_utm_nad83(self):
        return self.transform(self.utm_nad83)


def transform_coordinate(entrance):
    return TransformedCoordinate(entrance.datum, entrance.utmzone.utm_zone, \
                                 entrance.utmzone.utm_north, entrance.utmeast, entrance.utmnorth, \
                                 entrance.longitude, entrance.latitude)
