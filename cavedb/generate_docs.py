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
import csv
import osgeo.osr
from django.http import HttpResponseRedirect, Http404
from cavedb.docgen_composite import Composite
import cavedb.docgen_dvd
import cavedb.docgen_entrance_csv
import cavedb.docgen_gis_maps
import cavedb.docgen_gpx
import cavedb.docgen_kml
import cavedb.docgen_latex_letter_bw
import cavedb.docgen_latex_letter_color
import cavedb.docgen_latex_letter_draft
import cavedb.docgen_mapserver_mapfile
import cavedb.docgen_mxf
import cavedb.docgen_shp
import cavedb.docgen_text
import cavedb.docgen_todo_txt
import cavedb.models
import cavedb.perms
import cavedb.settings
import cavedb.utils

# Documents that span a single bulletin
def create_bulletin_docgen_classes(bulletin):
    return Composite([cavedb.docgen_dvd.create_for_bulletin(bulletin),
                      cavedb.docgen_entrance_csv.create_for_bulletin(bulletin),
                      cavedb.docgen_gpx.create_for_bulletin(bulletin),
                      cavedb.docgen_kml.create_for_bulletin(bulletin),
                      cavedb.docgen_mxf.create_for_bulletin(bulletin),
                      cavedb.docgen_text.Text(bulletin),
                      cavedb.docgen_todo_txt.TodoTxt(bulletin),

                      # The SHP and mapserver files need to be created before the GisMaps.
                      cavedb.docgen_shp.create_for_bulletin(bulletin),
                      cavedb.docgen_mapserver_mapfile.MapserverMapfile(bulletin),
                      cavedb.docgen_gis_maps.GisMaps(bulletin),

                      # Create the LaTeX PDFs last since they depend on other resources.
                      cavedb.docgen_latex_letter_draft.LatexLetterDraft(bulletin),
                      cavedb.docgen_latex_letter_bw.LatexLetterBW(bulletin),
                      cavedb.docgen_latex_letter_color.LatexLetterColor(bulletin),
                     ])


# Documents that span all bulletins
def create_global_docgen_classes():
    return Composite([cavedb.docgen_entrance_csv.create_for_global(),
                      cavedb.docgen_gpx.create_for_global(),
                      cavedb.docgen_kml.create_for_global(),
                      cavedb.docgen_mxf.create_for_global(),
                      cavedb.docgen_shp.create_for_global(),
                     ])


def get_bulletin_download_links(bulletin):
    docgen = create_bulletin_docgen_classes(bulletin)
    return docgen.create_html_download_urls()


def write_bulletin_files(bulletin):
    outputter = create_bulletin_docgen_classes(bulletin)

    all_regions_gis_hash = get_all_regions_gis_hash(bulletin.id)

    outputter.open(all_regions_gis_hash)

    outputter.indexed_terms(get_indexed_terms(bulletin))

    write_gis_sections(bulletin.id, outputter)

    outputter.begin_regions()

    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        write_region(region, outputter)

    outputter.end_regions()

    outputter.close()

    write_build_scripts(bulletin.id, outputter)


def write_global_bulletin_files():
    outputter = create_global_docgen_classes()

    outputter.open(None)

    outputter.indexed_terms([])

    # No GIS section. Only write that on the bulletin.

    outputter.begin_regions()

    for bulletin in cavedb.models.Bulletin.objects.all():
        for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin.id):
            write_region(region, outputter)

    outputter.end_regions()

    outputter.close()

    write_build_scripts(cavedb.utils.GLOBAL_BULLETIN_ID, outputter)


def write_build_scripts(bulletin_id, outputter):
    # Write two different build scripts. The first is a wrapper for the second
    # script. The first one is not run with -e so that the lockfile is properly
    # cleaned up. The second script is ran with -e so that the script will fail
    # if any commands fail. The web interface checks for the presence of this
    # lockfile to see if the bulletin documents are currently being generated.

    build_script_wrapper_file = cavedb.utils.get_build_script_wrapper(bulletin_id)
    build_lock_file = cavedb.utils.get_build_lock_file(bulletin_id)
    build_script_file = cavedb.utils.get_build_script(bulletin_id)
    build_log_file = cavedb.utils.get_build_log_filename(bulletin_id)

    with open(build_script_wrapper_file, 'w') as output:
        output.write('#!/bin/bash\n')
        output.write('touch %s\n' % (build_lock_file))
        output.write('%s > %s 2>&1\n' % (build_script_file, build_log_file))
        output.write('rm -f %s\n' % (build_lock_file))
    os.chmod(build_script_wrapper_file, 0755)

    build_script = outputter.generate_buildscript()

    with open(build_script_file, 'w') as output:
        output.write('#!/bin/bash -ev\n')
        output.write(build_script)
    os.chmod(build_script_file, 0755)


def write_region(region, outputter):
    gis_region_hash = get_region_gis_hash(region.id)

    outputter.begin_region(region, gis_region_hash)

    for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
        write_feature(feature, outputter)

    outputter.end_region()


def add_gis_lineplot(lineplot, gisdir, lineplot_type, outputter):
    zipfile_name = '%s/%s' % (cavedb.settings.MEDIA_ROOT, lineplot.attach_zip)

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


def write_gis_sections(bulletin_id, outputter):
    outputter.begin_gis_maps()
    for gismap in cavedb.models.GisMap.objects.all():
        outputter.gis_map(gismap)
    outputter.end_gis_maps()

    outputter.begin_gis_layers()

    for layer in cavedb.models.GisLayer.objects.all():
        outputter.gis_layer(layer)

    lineplots_dir = '%s/lineplots' % \
                    (cavedb.docgen_gis_common.get_bulletin_shp_directory(bulletin_id))
    if not os.path.isdir(lineplots_dir):
        os.makedirs(lineplots_dir)

    # Write out a CSV file that contains a description of all of the lineplots
    # These lineplots will be included with the SHP ZIP file.
    csvfile = open('%s/lineplots.csv' % (lineplots_dir), 'w')
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(['id', 'type', 'description', 'datum', 'coordinate_system'])

    # Expand cave and surface lineplots
    for lineplot in cavedb.models.BulletinGisLineplot.objects.filter(bulletin__id=bulletin_id):
        gisdir = '%s/bulletin_lineplot_%s' % (lineplots_dir, lineplot.id)
        add_gis_lineplot(lineplot, gisdir, 'surface', outputter)

        csvwriter.writerow(['bulletin_%s' % (lineplot.id), 'surface', lineplot.description, \
                            lineplot.datum, lineplot.coord_sys])


    for lineplot in cavedb.models.FeatureGisLineplot.objects \
       .filter(feature__bulletin_region__bulletin__id=bulletin_id):

        gisdir = '%s/feature_lineplot_%s' % (lineplots_dir, lineplot.id)
        add_gis_lineplot(lineplot, gisdir, 'underground', outputter)

        csvwriter.writerow(['feature_%s' % (lineplot.id), 'underground', lineplot.description, \
                            lineplot.datum, lineplot.coord_sys])

    csvfile.close()

    outputter.end_gis_layers()


class FeatureTodoAnalyzer(object):
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


class TransformedCoordinates(object):
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
    (newx, newy, _) = transformer.TransformPoint(xcoord, ycoord)

    return (newx, newy)


def get_nad27(in_srs, utmzone, xcoord, ycoord):
    out_srs = osgeo.osr.SpatialReference()
    out_srs.SetUTM(utmzone.utm_zone, utmzone.utm_north)
    out_srs.SetWellKnownGeogCS('NAD27')

    transformer = osgeo.osr.CoordinateTransformation(in_srs, out_srs)

    (newx, newy, _) = transformer.TransformPoint(xcoord, ycoord)
    return (newx, newy)


def get_region_gis_hash(region_id):
    has_entrances = False

    md5hash = hashlib.md5()
    for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region_id):
        for entrance in cavedb.models.FeatureEntrance.objects.filter(feature=feature.id):
            if not entrance.publish_location:
                continue

            coordinates = transform_coordinate(entrance)
            if not coordinates.wgs84_lat or not coordinates.wgs84_lon:
                continue

            has_entrances = True
            entranceinfo = '%s,%s,%s,%s,%s,%s,%s,%s,%s' % \
                           (feature.name, feature.feature_type, feature.is_significant, \
                            entrance.entrance_name, coordinates.utmzone, \
                            coordinates.nad27_utmeast, coordinates.nad27_utmnorth, \
                            coordinates.wgs84_lat, coordinates.wgs84_lon)
            md5hash.update(entranceinfo)

    return md5hash.hexdigest() if has_entrances else None


def get_all_regions_gis_hash(bulletin_id):
    has_entrances = False

    md5 = hashlib.md5()
    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin_id):
        gis_region_hash = get_region_gis_hash(region.id)
        if gis_region_hash:
            md5.update(gis_region_hash)
            has_entrances = True

    return md5.hexdigest() if has_entrances else None


def get_indexed_terms(bulletin):
    indexed_terms = []

    if bulletin.indexed_terms:
        for search_term in cavedb.utils.newline_split(bulletin.indexed_terms):
            indexed_terms.append(search_term)

    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
            indexed_terms.append(feature.name.strip())

            for alias in cavedb.utils.get_all_feature_alt_names(feature):
                indexed_terms.append(alias)

    return indexed_terms


def close_all_fds():
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = subprocess.MAXFD

    for filed in range(3, maxfd):
        try:
            os.close(filed)
        except OSError:
            pass


def run_buildscript_wrapper(bulletin_id):
    #pylint: disable=protected-access

    build_script_wrapper_file = cavedb.utils.get_build_script_wrapper(bulletin_id)

    # Rebuild the bulletin
    pid1 = os.fork()
    if pid1 == 0:
        os.setsid()
        close_all_fds()

        pid2 = os.fork()
        if pid2 == 0:
            basedir = '%s/bulletins/bulletin_%s' % (cavedb.settings.MEDIA_ROOT, bulletin_id)
            os.chdir(basedir)
            status = os.system('%s' % (build_script_wrapper_file))

            os._exit(status)
        else:
            os._exit(0)


def generate_bulletin(request, bulletin_id):
    #pylint: disable=unused-argument
    if not cavedb.perms.is_bulletin_generation_allowed(bulletin_id):
        raise Http404

    bulletins = cavedb.models.Bulletin.objects.filter(id=bulletin_id)
    if bulletins.count() == 0:
        raise Http404

    bulletin = bulletins[0]

    write_bulletin_files(bulletin)
    run_buildscript_wrapper(bulletin_id)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (cavedb.settings.CONTEXT_PATH))
