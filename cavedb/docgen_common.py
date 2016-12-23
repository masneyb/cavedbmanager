# Copyright 2007-2016 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

import os
import os.path

class Common:
    def __init__(self, basedir, bulletin):
        self.basedir = basedir
        self.bulletin = bulletin


    def open(self, all_regions_gis_hash):
        pass


    def close(self):
        pass


    def begin_gis_maps(self):
        pass


    def gis_map(self, gismap):
        pass


    def end_gis_maps(self):
        pass


    def begin_gis_layers(self):
        pass


    def gis_layer(self, gislayer):
        pass


    def gis_lineplot(self, lineplot, lineplot_type, shpfilename):
        pass


    def end_gis_layers(self):
        pass


    def begin_region(self, region, gis_region_hash, map_name):
        pass


    def end_region(self):
        pass


    def begin_feature(self, feature):
        pass


    def feature_todo(self, todo_enum, todo_descr):
        pass


    def feature_entrance(self, feature, ent, utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, \
                         wgs84_lon):
        pass


    def feature_attachment(self, feature, attachment):
        pass


    def feature_photo(self, feature, photo):
        pass


    def feature_referenced_map(self, feature, refmap):
        pass


    def feature_reference(self, feature, ref):
        pass


    def end_feature(self):
        pass


    def create_directory(self, suffix):
        outdir = self.basedir + suffix
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

