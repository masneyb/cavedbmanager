# SPDX-License-Identifier: Apache-2.0

import cavedb.docgen_common

class Composite(cavedb.docgen_common.Common):
    # pylint: disable=too-many-public-methods

    def __init__(self, composites):
        cavedb.docgen_common.Common.__init__(self)
        self.composites = composites


    def open(self, all_regions_gis_hash):
        for composite in self.composites:
            composite.open(all_regions_gis_hash)


    def close(self):
        for composite in self.composites:
            composite.close()


    def indexed_terms(self, terms):
        for composite in self.composites:
            composite.indexed_terms(terms)


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


    def begin_regions(self, chapters):
        for composite in self.composites:
            composite.begin_regions(chapters)


    def end_regions(self):
        for composite in self.composites:
            composite.end_regions()


    def begin_region(self, region, gis_region_hash):
        for composite in self.composites:
            composite.begin_region(region, gis_region_hash)


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


    def create_html_download_urls(self):
        ret = ''
        for composite in self.composites:
            composite_ret = composite.create_html_download_urls()
            if composite_ret:
                ret = composite_ret + ret

        return ret
