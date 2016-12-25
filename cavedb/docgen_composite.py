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

import cavedb.docgen_common

class Composite(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin, composites):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)
        self.composites = composites


    def open(self, all_regions_gis_hash):
        for composite in self.composites:
            composite.open(all_regions_gis_hash)


    def close(self):
        for composite in self.composites:
            composite.close()


    def begin_gis_maps(self):
        for composite in self.composites:
            composite.begin_gis_maps()


    def gis_map(self, gismap):
        for composite in self.composites:
            composite.gis_map(gismap)


    def end_gis_maps(self):
        for composite in self.composites:
            composite.end_gis_maps()


    def begin_gis_layers(self):
        for composite in self.composites:
            composite.begin_gis_layers()


    def gis_layer(self, gislayer):
        for composite in self.composites:
            composite.gis_layer(gislayer)


    def gis_lineplot(self, lineplot, lineplot_type, shpfilename):
        for composite in self.composites:
            composite.gis_lineplot(lineplot, lineplot_type, shpfilename)


    def end_gis_layers(self):
        for composite in self.composites:
            composite.end_gis_layers()


    def begin_region(self, region, gis_region_hash, map_name):
        for composite in self.composites:
            composite.begin_region(region, gis_region_hash, map_name)


    def end_region(self):
        for composite in self.composites:
            composite.end_region()


    def begin_feature(self, feature):
        for composite in self.composites:
            composite.begin_feature(feature)


    def feature_todo(self, feature, todo_enum, todo_descr):
        for composite in self.composites:
            composite.feature_todo(feature, todo_enum, todo_descr)


    def feature_entrance(self, feature, entrance, coordinates):
        for composite in self.composites:
            composite.feature_entrance(feature, entrance, coordinates)


    def feature_attachment(self, feature, attachment):
        for composite in self.composites:
            composite.feature_attachment(feature, attachment)


    def feature_photo(self, feature, photo):
        for composite in self.composites:
            composite.feature_photo(feature, photo)


    def feature_referenced_map(self, feature, refmap):
        for composite in self.composites:
            composite.feature_referenced_map(feature, refmap)


    def feature_reference(self, feature, ref):
        for composite in self.composites:
            composite.feature_reference(feature, ref)


    def end_feature(self):
        for composite in self.composites:
            composite.end_feature()


    def generate_buildscript(self):
        ret = ''
        for composite in self.composites:
            composite_ret = composite.generate_buildscript()
            if composite_ret:
                if ret:
                    ret = '%s\n%s' % (ret, composite_ret)
                else:
                    ret = composite_ret

        return ret

