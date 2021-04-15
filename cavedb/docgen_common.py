# SPDX-License-Identifier: Apache-2.0

import os
import os.path
from django.conf import settings
import cavedb.utils

# pylint: disable=no-self-use,too-many-public-methods
class Common(object):
    def __init__(self):
        pass


    def open(self, all_regions_gis_hash):
        pass


    def close(self):
        pass


    def indexed_terms(self, terms):
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


    def begin_regions(self, chapters):
        pass


    def end_regions(self):
        pass


    def begin_region(self, region, gis_region_hash):
        pass


    def end_region(self):
        pass


    def begin_feature(self, feature):
        pass


    def feature_todo(self, feature, todo_enum, todo_descr):
        pass


    def feature_entrance(self, feature, entrance, coordinates):
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


    def generate_buildscript(self):
        return None


    def create_html_download_urls(self):
        return None


    def create_url(self, url_suffix, description, localfile):
        if not url_suffix:
            return None

        url = '%s%s' % (settings.MEDIA_URL, url_suffix)
        return '<a href="%s">%s</a> [%s]<br/>\n' % \
                   (url, description, cavedb.utils.get_file_size(localfile))




def create_directory(outdir):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)


def create_base_directory(filename):
    outdir = os.path.dirname(filename)
    create_directory(outdir)


def get_entrance_name(feature, ent):
    if ent.entrance_name and feature.name != ent.entrance_name:
        return '%s - %s' % (feature.name, ent.entrance_name)

    return feature.name
