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

import hashlib
import os
import os.path
import resource
import subprocess
from zipfile import ZipFile
import osgeo.osr
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
import cavedb.models
import cavedb.utils
from cavedb.docgen_composite import Composite
import cavedb.docgen_entrance_csv
import cavedb.docgen_gpx
import cavedb.docgen_kml
import cavedb.docgen_mxf
import cavedb.docgen_text
import cavedb.docgen_todo_txt
import cavedb.docgen_xml

def write_bulletin_files(bulletin, basedir):
    outputter = Composite(basedir, bulletin,
                          [cavedb.docgen_entrance_csv.EntranceCsv(basedir, bulletin),
                           cavedb.docgen_gpx.Gpx(basedir, bulletin),
                           cavedb.docgen_kml.Kml(basedir, bulletin),
                           cavedb.docgen_mxf.Mxf(basedir, bulletin),
                           cavedb.docgen_text.Text(basedir, bulletin),
                           cavedb.docgen_todo_txt.TodoTxt(basedir, bulletin),
                           cavedb.docgen_xml.Xml(basedir, bulletin)])

    all_regions_gis_hash = get_all_regions_gis_hash(bulletin.id)

    outputter.open(all_regions_gis_hash)

    outputter.begin_gis_maps()
    for gismap in cavedb.models.GisMap.objects.all():
        outputter.gis_map(gismap)
    outputter.end_gis_maps()

    write_gis_section(bulletin.id, outputter)

    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        map_name = region.map_region_name
        if not map_name:
            map_name = region.region_name

        gis_region_hash = get_region_gis_hash(region.id)

        outputter.begin_region(region, gis_region_hash, map_name)

        for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
            write_feature(feature, outputter)

        outputter.end_region()

    outputter.close()


def add_gis_lineplot(lineplot, gisdir, lineplot_type, outputter):
    zipfile_name = '%s/%s' % (settings.MEDIA_ROOT, lineplot.attach_zip)

    if not os.path.isdir(gisdir):
        os.makedirs(gisdir)

    zipfile = ZipFile(zipfile_name, "r")
    for name in zipfile.namelist():
        if name.endswith('/'):
            continue

        base = os.path.basename(name)
        if base == '':
            base = name

        gisfile_name = '%s/%s' % (gisdir, base)
        gisfile = open(gisfile_name, 'w')
        gisfile.write(zipfile.read(name))
        gisfile.close()

    zipfile.close()

    outputter.gis_lineplot(lineplot, lineplot_type, '%s/%s' % (gisdir, lineplot.shp_filename))


def write_gis_section(bulletin_id, outputter):
    outputter.begin_gis_layers()

    for layer in cavedb.models.GisLayer.objects.all():
        outputter.gis_layer(layer)

    # Expand cave and surface lineplots
    for lineplot in cavedb.models.BulletinGisLineplot.objects.filter(bulletin__id=bulletin_id):
        gisdir = '%s/bulletins/bulletin_%s/output/lineplots/bulletin_lineplot_%s' % \
                 (settings.MEDIA_ROOT, lineplot.bulletin.id, lineplot.id)
        add_gis_lineplot(lineplot, gisdir, 'surface', outputter)


    for lineplot in cavedb.models.FeatureGisLineplot.objects \
       .filter(feature__bulletin_region__bulletin__id=bulletin_id):

        gisdir = '%s/bulletins/bulletin_%s/output/lineplots/feature_lineplot_%s' % \
                 (settings.MEDIA_ROOT, lineplot.feature.bulletin_region.bulletin.id, lineplot.id)
        add_gis_lineplot(lineplot, gisdir, 'underground', outputter)

    outputter.end_gis_layers()


class FeatureTodoAnalyzer:
    def __init__(self, feature):
        self.missing_str = ''
        self.missing_coord = False
        self.missing_ele = False
        self.saw_entrance = False
        self.has_map = False

        self.todo_descr = feature.todo_descr
        self.todo_enum = feature.todo_enum
        if not self.todo_enum:
            self.todo_enum = 'minor_computer_work'

        if not feature.survey_id:
            self.missing_str += ' ID'
        if not feature.description:
            self.missing_str += ' description'


    def process_entrance(self, ent):
        self.saw_entrance = True
        if not ent.elevation_ft:
            self.missing_ele = True

        if not ent.utmeast and not ent.longitude:
            self.missing_coord = True


    def process_photo(self, photo):
        if photo.type == 'map':
            self.has_map = True


    def process_referenced_map(self):
        self.has_map = True


    def write_todo(self, feature, outputter):
        if self.missing_coord or not self.saw_entrance:
            self.missing_str += ' GPS'
            self.todo_enum = 'minor_field_work'
        elif self.missing_ele:
            self.missing_str += ' elevation'

        if self.missing_str:
            self.missing_str = 'The following fields are missing: (%s ).' % (self.missing_str)

            if not self.todo_descr:
                self.todo_descr = self.missing_str
            else:
                self.todo_descr = '%s %s' % (self.todo_descr, self.missing_str)

        if self.todo_descr:
            outputter.feature_todo(feature, self.todo_enum, self.todo_descr)


def write_feature(feature, outputter):
    todo = FeatureTodoAnalyzer(feature)

    outputter.begin_feature(feature)

    for ent in cavedb.models.FeatureEntrance.objects.filter(feature=feature.id):
        if not ent.publish_location:
            continue

        coordinates = transform_coordinate(ent)

        outputter.feature_entrance(feature, ent, coordinates)
        todo.process_entrance(ent)

    for attachment in cavedb.models.FeatureAttachment.objects.filter(feature__id=feature.id):
        outputter.feature_attachment(feature, attachment)

    for photo in cavedb.models.FeaturePhoto.objects.filter(feature__id=feature.id):
        outputter.feature_photo(feature, photo)
        todo.process_photo(photo)

    for refmap in cavedb.models.FeatureReferencedMap.objects\
       .filter(feature__id=feature.id, map__show_in_pdf=True):

        outputter.feature_referenced_map(feature, refmap)
        todo.process_referenced_map()

    for ref in cavedb.models.FeatureReference.objects.filter(feature=feature.id):
        outputter.feature_reference(feature, ref)

    todo.write_todo(feature, outputter)
    outputter.end_feature()


class TransformedCoordinates:
    def __init__(self):
        self.utmzone, self.nad27_utmeast, self.nad27_utmnorth = '', '', ''
        self.wgs84_lat, self.wgs84_lon = '', ''


def transform_coordinate(entrance):
    coords = TransformedCoordinates()

    coords.utmzone = entrance.utmzone

    in_srs = osgeo.osr.SpatialReference()
    in_srs.SetWellKnownGeogCS(entrance.datum.encode('ascii'))

    if entrance.utmeast != None and entrance.utmeast != 0 and entrance.utmnorth != None and \
       entrance.utmnorth != 0:
        in_srs.SetUTM(entrance.utmzone.utm_zone, entrance.utmzone.utm_north)

        (coords.wgs84_lon, coords.wgs84_lat) = get_wgs84(in_srs, \
                                                         int(entrance.utmeast), \
                                                         int(entrance.utmnorth))

        (coords.nad27_utmeast, coords.nad27_utmnorth) = get_nad27(in_srs, \
                                                                  entrance.utmzone, \
                                                                  int(entrance.utmeast), \
                                                                  int(entrance.utmnorth))

    elif entrance.longitude != None and entrance.longitude != 0 and \
         entrance.latitude != None and entrance.latitude != 0:
        (coords.wgs84_lon, coords.wgs84_lat) = get_wgs84(in_srs, \
                                                         float(entrance.longitude), \
                                                         float(entrance.latitude))

        (coords.nad27_utmeast, coords.nad27_utmnorth) = get_nad27(in_srs, \
                                                                  entrance.utmzone, \
                                                                  float(entrance.longitude), \
                                                                  float(entrance.latitude))

    return coords


def get_wgs84(in_srs, xcoord, ycoord):
    out_srs = osgeo.osr.SpatialReference()
    out_srs.SetWellKnownGeogCS('WGS84')

    transformer = osgeo.osr.CoordinateTransformation(in_srs, out_srs)
    (newx, newy, newz) = transformer.TransformPoint(xcoord, ycoord)

    return (newx, newy)


def get_nad27(in_srs, utmzone, xcoord, ycoord):
    out_srs = osgeo.osr.SpatialReference()
    out_srs.SetUTM(utmzone.utm_zone, utmzone.utm_north)
    out_srs.SetWellKnownGeogCS('NAD27')

    transformer = osgeo.osr.CoordinateTransformation(in_srs, out_srs)

    (newx, newy, newz) = transformer.TransformPoint(xcoord, ycoord)
    return (newx, newy)


def get_region_gis_hash(region_id):
    md5hash = hashlib.md5()
    for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region_id):
        for entrance in cavedb.models.FeatureEntrance.objects.filter(feature=feature.id):
            if not entrance.publish_location:
                continue

            coordinates = transform_coordinate(entrance)

            entranceinfo = '%s,%s,%s,%s,%s,%s,%s,%s,%s' % \
                           (feature.name, feature.feature_type, feature.is_significant, \
                            entrance.entrance_name, coordinates.utmzone, \
                            coordinates.nad27_utmeast, coordinates.nad27_utmnorth, \
                            coordinates.wgs84_lat, coordinates.wgs84_lon)
            md5hash.update(entranceinfo)

    return md5hash.hexdigest()


def get_all_regions_gis_hash(bulletin_id):
    md5 = hashlib.md5()
    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin_id):
        gis_region_hash = get_region_gis_hash(region.id)
        md5.update(gis_region_hash)

    return md5.hexdigest()


def write_makefile(bulletin_id, basedir):
    filename = '%s/Makefile' % (basedir)
    makefile = open(filename, 'w')

    makefile.write('DOCPREFIX=bulletin_%s\n' % (bulletin_id))
    makefile.write('DOC_BASE_DIR=$(shell pwd)\n')
    makefile.write('OUTPUTDIR=$(DOC_BASE_DIR)/output\n')
    makefile.write('TEMPLATE_BASE_DIR=$(DOC_BASE_DIR)/../base_bulletin\n')
    makefile.write('include $(TEMPLATE_BASE_DIR)/Makefile.include\n')

    makefile.close()


def close_all_fds():
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = subprocess.MAXFD

    for filed in range(3, maxfd):
        try:
            os.close(filed)
        except OSError:
            pass


def write_buildscript(basedir):
    filename = '%s/build' % (basedir)
    buildscriptfile = open(filename, 'w')

    # This lockfile is checked by the web interface to see if a build is
    # in progress.

    buildscriptfile.write('#!/bin/bash\n')
    buildscriptfile.write('touch build-in-progress.lock\n')
    buildscriptfile.write('make\n')
    buildscriptfile.write('rm -f build-in-progress.lock\n')

    buildscriptfile.close()
    os.chmod(filename, 0755)


def run_make_command(basedir):
    # Rebuild the bulletin
    pid1 = os.fork()
    if pid1 == 0:
        os.setsid()
        close_all_fds()

        pid2 = os.fork()
        if pid2 == 0:
            os.chdir(basedir)
            status = os.system('./build > bulletin-build-output.txt 2>&1')

            os._exit(status)
        else:
            os._exit(0)


def generate_bulletin(request, bulletin_id):
    if not cavedb.utils.is_bulletin_generation_allowed(bulletin_id):
        raise Http404

    bulletins = cavedb.models.Bulletin.objects.filter(id=bulletin_id)
    if bulletins.count() == 0:
        raise Http404

    bulletin = bulletins[0]
    basedir = '%s/bulletins/bulletin_%s' % (settings.MEDIA_ROOT, bulletin_id)

    write_bulletin_files(bulletin, basedir)
    write_makefile(bulletin_id, basedir)
    write_buildscript(basedir)
    run_make_command(basedir)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))


def generate_bulletin_source(request, bulletin_id):
    if not cavedb.utils.is_bulletin_generation_allowed(bulletin_id):
        raise Http404

    bulletins = cavedb.models.Bulletin.objects.filter(id=bulletin_id)
    if bulletins.count() == 0:
        raise Http404

    bulletin = bulletins[0]
    basedir = '%s/bulletins/bulletin_%s' % (settings.MEDIA_ROOT, bulletin_id)

    write_bulletin_files(bulletin, basedir)
    write_makefile(bulletin_id, basedir)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))

def generate_all_bulletin_sources(request):
    for bulletin in cavedb.models.Bulletin.objects.all():
        if not cavedb.utils.is_bulletin_generation_allowed(bulletin.id):
            continue

        generate_bulletin_source(request, bulletin.id)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))

