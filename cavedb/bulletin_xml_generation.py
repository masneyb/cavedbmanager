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
import re
import resource
import subprocess
from xml.sax.saxutils import escape
from zipfile import ZipFile
import datetime
import dateutil.parser
import dateutil.relativedelta
import osgeo.osr
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
import cavedb.models
import cavedb.utils

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


def transform_coordinate(entrance):
    utmzone = entrance.utmzone
    nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon = '', '', '', ''

    in_srs = osgeo.osr.SpatialReference()
    in_srs.SetWellKnownGeogCS(entrance.datum.encode('ascii'))

    if entrance.utmeast != None and entrance.utmeast != 0 and entrance.utmnorth != None and \
       entrance.utmnorth != 0:
        in_srs.SetUTM(entrance.utmzone.utm_zone, entrance.utmzone.utm_north)

        (wgs84_lon, wgs84_lat) = get_wgs84(in_srs, int(entrance.utmeast), int(entrance.utmnorth))
        (nad27_utmeast, nad27_utmnorth) = get_nad27(in_srs, entrance.utmzone, \
                                                    int(entrance.utmeast), \
                                                    int(entrance.utmnorth))

    elif entrance.longitude != None and entrance.longitude != 0 and entrance.latitude != None and \
         entrance.latitude != 0:
        (wgs84_lon, wgs84_lat) = get_wgs84(in_srs, float(entrance.longitude), \
                                           float(entrance.latitude))
        (nad27_utmeast, nad27_utmnorth) = get_nad27(in_srs, entrance.utmzone, \
                                                    float(entrance.longitude), \
                                                    float(entrance.latitude))

    return utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon


def get_normalized_date(datestr):
    # Parse different date formats including:
    # Sep 21, 1997, Fall/Winter 1997, Fall 1997, etc.

    if not datestr:
        return "0000-00-00"

    pattern = re.compile(r'/[\w\d]+')
    datestr = pattern.sub('', datestr)

    datestr = datestr.replace("Spring", "April")
    datestr = datestr.replace("Summer", "July")
    datestr = datestr.replace("Fall", "October")
    datestr = datestr.replace("Winter", "January")

    try:
        defaults = datetime.datetime.now() + \
                   dateutil.relativedelta.relativedelta(month=1, day=1, hour=0, minute=0, \
                                                        second=0, microsecond=0)
        return dateutil.parser.parse(datestr, default=defaults)
    except ValueError:
        return "0000-00-00"


def convert_quotes(inputstr):
    # Directional quote support for LaTeX
    # FIXME - put this in the xml2latex.xsl stylesheet

    if not inputstr:
        return ""

    inputstr = inputstr.strip()
    inputstr = inputstr.replace(" - ", " -- ")

    while True:
        if inputstr.count("\"") < 2:
            break

        inputstr = inputstr.replace("\"", "``", 1)
        inputstr = inputstr.replace("\"", "''", 1)

    return escape(inputstr)


def clean_index(inputstr):
    # FIXME - ugly hack until Tucker County book is published
    inputstr = inputstr.replace(r"\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of Cheat River}", \
                          r"\caveindex{Great Cave of Dry Fork of Cheat River}")
    inputstr = inputstr.replace(r"\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of \caveindex{Cheat River}}", \
                          r"\caveindex{Great Cave of Dry Fork of Cheat River}")

    flags = re.MULTILINE | re.DOTALL | re.VERBOSE
    result = re.compile(r'(.*?)(\\caveindex{)(.*?)}(.*)', flags).match(inputstr)
    if not result:
        return inputstr
    elif re.compile(r'^\\caveindex{.*', flags).match(result.group(3)):
        value = re.sub(r'^\\caveindex{', '', result.group(3))
        return '%s%s%s%s' % (result.group(1), result.group(2), value, clean_index(result.group(4)))
    elif not re.compile(r'^.*\\caveindex.*$', flags).match(result.group(3)):
        if re.compile(r'^.*\\caveindex.*$', flags).match(result.group(4)):
            return '%s%s%s}%s' % (result.group(1), result.group(2), result.group(3), \
                                  clean_index(result.group(4)))
        else:
            return inputstr
    else:
        value = re.sub(r'^(.*?)\s\\caveindex{(.*)', r'\1 \2', result.group(3))
        return '%s%s' % (result.group(1),
                         clean_index('%s%s%s' % (result.group(2), value, result.group(4))))


def finalize_index(inputstr, indexed_terms):
    flags = re.MULTILINE | re.DOTALL | re.VERBOSE
    result = re.compile(r'(.*?)\\caveindex{(.*?)}(.*)', flags).match(inputstr)
    if not result:
        return inputstr

    return '%s%s%s' % (result.group(1), indexed_terms[1][result.group(2)], \
                       finalize_index(result.group(3), indexed_terms))


def generate_index(inputstr, indexed_terms):
    # Add terms to the index
    for term in indexed_terms[0]:
        # This appears to be quicker than doing a single regular expression
        inputstr = inputstr.replace('%s ' % (term), r'\caveindex{%s} ' % (term))
        inputstr = inputstr.replace('%s.' % (term), r'\caveindex{%s}.' % (term))
        inputstr = inputstr.replace('%s,' % (term), r'\caveindex{%s},' % (term))
        inputstr = inputstr.replace('%s:' % (term), r'\caveindex{%s}:' % (term))
        inputstr = inputstr.replace('%s)' % (term), r'\caveindex{%s})' % (term))
        inputstr = inputstr.replace('%s\'' % (term), r'\caveindex{%s}\'' % (term))
        #inputstr = re.sub(r'([\s\.,]*)(' + term + r')([\s\.\,]*)', r'\1\caveindex{\2}\3', inputstr)

    return finalize_index(clean_index(inputstr), indexed_terms)


def convert_nl_to_para(inputstr):
    inputstr = convert_quotes(inputstr)
    ret = ''
    for para in inputstr.split('\n'):
        para = para.replace('\r', '')
        if para == '':
            continue

        ret = '%s<para>%s</para>' % (ret, para)

    return ret


# Add a \hbox{} around the cave and entrance names so that they appear on the
# same line in the PDF.
def add_caption_hbox(caption, name):
    if caption.startswith(name):
        return caption

    return caption.replace(name, r'\hbox{%s}' % (name))


def format_photo_caption(feature, caption):
    caption = add_caption_hbox(caption, feature.name)

    if feature.alternate_names:
        for alias in feature.alternate_names.split(','):
            alias = alias.strip()
            if alias != "":
                caption = add_caption_hbox(caption, alias)

    if feature.additional_index_names:
        for alias in feature.additional_index_names.split(','):
            alias = alias.strip()
            if alias != "":
                caption = add_caption_hbox(caption, alias)

    for entrance in cavedb.models.FeatureEntrance.objects.filter(feature=feature.id):
        if entrance.entrance_name:
            caption = add_caption_hbox(caption, entrance.entrance_name)

    return convert_quotes(caption)


def write_feature(xmlfile, feature, indexed_terms):
    missing_str = ''

    todo_descr = feature.todo_descr
    todo_enum = feature.todo_enum
    if not todo_enum:
        todo_enum = 'minor_computer_work'

    feature_att_str = 'type="%s" internal_id="%s"' % (feature.feature_type, feature.id)

    if feature.is_significant:
        feature_att_str = '%s significant="yes"' % (feature_att_str)
    else:
        feature_att_str = '%s significant="no"' % (feature_att_str)

    if feature.cave_sign_installed:
        feature_att_str = '%s cave_sign_installed="yes"' % (feature_att_str)
    else:
        feature_att_str = '%s cave_sign_installed="no"' % (feature_att_str)

    if feature.survey_id:
        feature_att_str = '%s survey_prefix="%s" survey_suffix="%s" id="%s%s"' % \
                          (feature_att_str, feature.survey_county.survey_short_name, \
                           feature.survey_id, feature.survey_county.survey_short_name, \
                           feature.survey_id)
    else:
        missing_str += ' ID'

    xmlfile.write('<feature %s>\n' % (feature_att_str))

    xmlfile.write('<name>%s</name>\n' % (feature.name.strip()))

    if feature.alternate_names:
        for alias in feature.alternate_names.split(','):
            alias = alias.strip()
            if alias:
                xmlfile.write('<aliases>%s</aliases>\n' % (alias))

    if feature.additional_index_names:
        for alias in feature.additional_index_names.split(','):
            alias = alias.strip()
            if alias:
                xmlfile.write('<additional_index_name>%s</additional_index_name>\n' % (alias))

    # For debugging coordinate problems...
    xmlfile.flush()

    missing_coord = False
    missing_ele = False
    saw_entrance = False

    for ent in cavedb.models.FeatureEntrance.objects.filter(feature=feature.id):
        if not ent.publish_location:
            continue

        saw_entrance = True
        if not ent.elevation_ft:
            missing_ele = True

        utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon = transform_coordinate(ent)

        attstr = ''
        if ent.entrance_name:
            attstr += ' name="%s"' % (ent.entrance_name)

        if ent.access_enum:
            attstr += ' access_status="%s"' % (ent.access_enum)

        if ent.coord_acquision:
            attstr += ' coord_acquision="%s"' % (ent.coord_acquision)

        if nad27_utmeast != '' and nad27_utmeast != 0:
            quad_name = ''
            if ent.quad:
                quad_name = ent.quad

            xmlfile.write('<location%s id="%s" wgs84_lat="%s" wgs84_lon="%s" utmzone="%s" utm27_utmeast="%s" utm27_utmnorth="%s" ele="%s" county="%s" quad="%s"/>\n' % \
                          (attstr, ent.id, wgs84_lat, wgs84_lon, utmzone, nad27_utmeast, \
                           nad27_utmnorth, ent.elevation_ft, ent.county, quad_name))
        else:
            missing_coord = True

    if missing_coord or not saw_entrance:
        missing_str += ' GPS'
        todo_enum = 'minor_field_work'
    elif missing_ele:
        missing_str += ' elevation'

    for attachment in cavedb.models.FeatureAttachment.objects.filter(feature__id=feature.id):
        attrs = 'filename="%s" type="%s"' % (attachment.attachment, attachment.attachment_type)
        if attachment.description:
            attrs += ' description="%s"' % (convert_quotes(attachment.description))
        if attachment.user_visible_file_suffix:
            attrs += ' user_visible_file_suffix="%s"' % \
                     (convert_quotes(attachment.user_visible_file_suffix))
        if attachment.author:
            attrs += ' author="%s"' % (convert_quotes(attachment.author))

        xmlfile.write('<attachment %s/>\n' % (attrs))

    has_map = False
    num_in_pdf = 1
    for photo in cavedb.models.FeaturePhoto.objects.filter(feature__id=feature.id):
        attrs = 'id="photo%s" type="%s" scale="%s" rotate="%s" base_directory="%s" primary_filename="%s" secondary_filename="%s" sort_order="%s" show_at_end="%s" include_on_dvd="%s" show_in_pdf="%s"' % \
                (photo.id, photo.type, photo.scale, photo.rotate_degrees, settings.MEDIA_ROOT, \
                 photo.filename, photo.secondary_filename, photo.sort_order, \
                 int(photo.show_at_end), int(photo.include_on_dvd), int(photo.show_in_pdf))

        if photo.show_in_pdf:
            attrs += ' num_in_pdf="%s"' % (num_in_pdf)
            num_in_pdf = num_in_pdf + 1
        if photo.caption:
            attrs += ' caption="%s"' % (format_photo_caption(feature, photo.caption))
        if photo.people_shown:
            attrs += ' people_shown="%s"' % (convert_quotes(photo.people_shown))
        if photo.author:
            attrs += ' author="%s"' % (convert_quotes(photo.author))

        xmlfile.write('<photo %s>\n' % (attrs))

        if photo.indexed_terms:
            for term in photo.indexed_terms.split('\n'):
                xmlfile.write('<index>%s</index>\n' % (term.strip()))

        xmlfile.write('</photo>\n')

        if photo.type == 'map':
            has_map = True

    for photo in cavedb.models.FeatureReferencedMap.objects.filter(feature__id=feature.id, map__show_in_pdf=True):
        xmlfile.write('<photo ref="photo%s" type="map" show_in_pdf="1" />\n' % (photo.map.id))
        has_map = True

    if feature.length_ft:
        xmlfile.write('<length>%s</length>\n' % (feature.length_ft))
        if not has_map and feature.length_ft >= 3000:
            missing_str += ' map'

    if feature.depth_ft:
        xmlfile.write('<depth>%s</depth>\n' % (feature.depth_ft))

    if feature.length_based_on:
        xmlfile.write('<length_based_on>%s</length_based_on>\n' % (feature.length_based_on))

    if feature.description:
        if feature.source:
            xmlfile.write('<desc author="%s">%s</desc>\n' % \
                    (convert_quotes(feature.source), \
                     generate_index(convert_nl_to_para(feature.description), indexed_terms)))
        else:
            xmlfile.write('<desc>%s</desc>\n' % \
                    (generate_index(convert_nl_to_para(feature.description), indexed_terms)))
    else:
        missing_str += ' description'

    if feature.history:
        xmlfile.write('<history>%s</history>\n' % \
                (generate_index(convert_quotes(feature.history), indexed_terms)))

    if feature.internal_history:
        xmlfile.write('<internal_history>%s</internal_history>\n' % \
                (generate_index(convert_quotes(feature.internal_history), indexed_terms)))

    if feature.biology:
        xmlfile.write('<biology>%s</biology>\n' % \
                (generate_index(convert_quotes(feature.biology), indexed_terms)))

    if feature.geology_hydrology:
        xmlfile.write('<geology>%s</geology>\n' % \
                (generate_index(convert_quotes(feature.geology_hydrology), indexed_terms)))

    if feature.hazards:
        xmlfile.write('<hazards>%s</hazards>\n' % \
                (generate_index(convert_quotes(feature.hazards), indexed_terms)))

    if feature.owner_name:
        xmlfile.write('<owner_name>%s</owner_name>\n' % (feature.owner_name))

    if feature.owner_address:
        xmlfile.write('<owner_address>%s</owner_address>\n' % (feature.owner_address))

    if feature.owner_phone:
        xmlfile.write('<owner_phone>%s</owner_phone>\n' % (feature.owner_phone))

    for ref in cavedb.models.FeatureReference.objects.filter(feature=feature.id):
        write_reference(xmlfile, ref)

    if feature.access_enum and feature.access_descr:
        xmlfile.write('<access status="%s">%s</access>\n' % \
                      (feature.access_enum, feature.access_descr))

    if missing_str:
        missing_str = 'The following fields are missing: (%s ).' % (missing_str)

        if not todo_descr:
            todo_descr = missing_str
        else:
            todo_descr = '%s %s' % (todo_descr, missing_str)

    if todo_descr:
        xmlfile.write('<bulletin_work category="%s">%s</bulletin_work>\n' % (todo_enum, todo_descr))

    xmlfile.write('</feature>\n')


def get_region_gis_hash(region_id):
    md5hash = hashlib.md5()
    for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region_id):
        for entrance in cavedb.models.FeatureEntrance.objects.filter(feature=feature.id):
            if not entrance.publish_location:
                continue

            utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon = \
               transform_coordinate(entrance)

            entranceinfo = '%s,%s,%s,%s,%s,%s,%s,%s,%s' % \
                           (feature.name, feature.feature_type, feature.is_significant, \
                            entrance.entrance_name, utmzone, nad27_utmeast, nad27_utmnorth, \
                            wgs84_lat, wgs84_lon)
            md5hash.update(entranceinfo)

    return md5hash.hexdigest()


def get_all_regions_gis_hash(bulletin_id):
    md5 = hashlib.md5()
    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin_id):
        gis_region_hash = get_region_gis_hash(region.id)
        md5.update(gis_region_hash)

    return md5.hexdigest()


def write_reference(xmlfile, ref):
    hidden_in_bibliography = ref.title.startswith('unpublished trip report') or \
                             ref.title.startswith('Tucker County Speleological Survey Files') or \
                             ref.title.startswith('personal communication') or \
                             ref.title.startswith('e-mail') or \
                             ref.title.startswith('letter to') or \
                             ref.title.startswith('Trip Report in NSS Files')

    xmlfile.write('<reference author="%s" title="%s" book="%s" volume="%s" number="%s" pages="%s" url="%s" date="%s" extra="%s" parsed_date="%s" hidden_in_bibliography="%s"/>\n' % \
                  (convert_quotes(ref.author), convert_quotes(ref.title), \
                   convert_quotes(ref.book), convert_quotes(ref.volume), \
                   convert_quotes(ref.number), convert_quotes(ref.pages), \
                   convert_quotes(ref.url), convert_quotes(ref.date), convert_quotes(ref.extra), \
                   get_normalized_date(ref.date), hidden_in_bibliography))


def get_indexed_terms(bulletin):
    indexed_terms = [], {}
    if bulletin.indexed_terms:
        for search_term in bulletin.indexed_terms.split('\n'):
            search_term = convert_quotes(search_term.replace('\r', '').strip())
            if not search_term:
                continue

            all_index_terms = search_term.split(':')
            if len(all_index_terms) == 1:
                indexed_terms[0].append(search_term)
                indexed_terms[1][search_term] = r'\index{%s}%s' % (search_term, search_term)
            else:
                replacement = ''
                for index_term in all_index_terms[1:]:
                    replacement = r'%s\index{%s}' % (replacement, index_term)
                indexed_terms[0].append(all_index_terms[0])
                indexed_terms[1][all_index_terms[0]] = '%s%s' % (replacement, all_index_terms[0])

    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
            feature_name = feature.name.strip()
            indexed_terms[0].append(feature_name)
            indexed_terms[1][feature_name] = r'\index{%s}%s' % (feature_name, feature_name)

            if feature.alternate_names:
                for alias in feature.alternate_names.split(','):
                    alias = alias.strip()
                    if alias:
                        indexed_terms[0].append(alias)
                        indexed_terms[1][alias] = r'\index{%s}%s' % (alias, alias)

            if feature.additional_index_names:
                for alias in feature.additional_index_names.split(','):
                    alias = alias.strip()
                    if alias:
                        indexed_terms[0].append(alias)
                        indexed_terms[1][alias] = r'\index{%s}%s' % (alias, alias)

    indexed_terms[0].sort(key=lambda term: len(term), reverse=True)

    return indexed_terms


def write_chapters(xmlfile, bulletin, indexed_terms):
    xmlfile.write('<chapters>\n')

    for chapter in cavedb.models.BulletinChapter.objects.filter(bulletin__id=bulletin.id):
        xmlfile.write('<chapter title="%s" is_appendix="%i">\n' % \
                (chapter.chapter_title, chapter.is_appendix))

        for section in cavedb.models.BulletinSection.objects.filter(bulletin_chapter__id=chapter.id):
            section_attrs = ''
            if section.section_title:
                section_attrs = '%s title="%s"' % (section_attrs, section.section_title)

            if section.section_subtitle:
                section_attrs = '%s subtitle="%s"' % (section_attrs, section.section_subtitle)

            xmlfile.write('<section%s>\n' % (section_attrs))
            xmlfile.write('<text num_columns="%s">%s</text>' % \
                    (section.num_columns, \
                     generate_index(convert_quotes(section.section_data), indexed_terms)))

            for ref in cavedb.models.BulletinSectionReference.objects.filter(bulletinsection__id=section.id):
                write_reference(xmlfile, ref)

            xmlfile.write('</section>\n')

        xmlfile.write('</chapter>')

    xmlfile.write('</chapters>\n')


def write_feature_indexes(xmlfile, bulletin):
    aliases = {}

    # Show all of the names and aliases in one place so that they can be sorted in the index
    xmlfile.write('<feature_indexes>\n')

    for feature in cavedb.models.Feature.objects.filter(bulletin_region__bulletin__id=bulletin.id):
        xmlfile.write('<index name="%s" is_primary="1"/>\n' % (feature.name.strip()))

        if feature.alternate_names:
            for alias in feature.alternate_names.split(','):
                alias = alias.strip()
                if alias:
                    if alias in aliases:
                        aliases[alias].append(feature.id)
                    else:
                        aliases[alias] = [feature.id]

        if feature.additional_index_names:
            for alias in feature.additional_index_names.split(','):
                alias = alias.strip()
                if alias:
                    if alias in aliases:
                        aliases[alias].append(feature.id)
                    else:
                        aliases[alias] = [feature.id]

    for alias in aliases:
        xmlfile.write('<index name="%s" is_alias="1">\n' % (alias))
        for feature_id in aliases[alias]:
            xmlfile.write('<feature_id>%s</feature_id>\n' % (feature_id))

        xmlfile.write('</index>\n')

    xmlfile.write('</feature_indexes>\n')


def write_all_references(xmlfile, bulletin):
    # Write out all references together for the bibliography
    xmlfile.write('<all_references>\n')

    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
            for ref in cavedb.models.FeatureReference.objects.filter(feature=feature.id):
                write_reference(xmlfile, ref)

    for chapter in cavedb.models.BulletinChapter.objects.filter(bulletin__id=bulletin.id):
        for section in cavedb.models.BulletinSection.objects.filter(bulletin_chapter__id=chapter.id):
            for ref in cavedb.models.BulletinSectionReference.objects.filter(bulletinsection__id=section.id):
                write_reference(xmlfile, ref)

    xmlfile.write('</all_references>\n')


def write_bulletin_maps(xmlfile, bulletin):
    if bulletin.bw_map1:
        xmlfile.write('<map type="black_and_white">%s</map>\n' % (bulletin.bw_map1))
    if bulletin.bw_map2:
        xmlfile.write('<map type="black_and_white">%s</map>\n' % (bulletin.bw_map2))
    if bulletin.bw_map3:
        xmlfile.write('<map type="black_and_white">%s</map>\n' % (bulletin.bw_map3))
    if bulletin.color_map1:
        xmlfile.write('<map type="color">%s</map>\n' % (bulletin.color_map1))
    if bulletin.color_map2:
        xmlfile.write('<map type="color">%s</map>\n' % (bulletin.color_map2))
    if bulletin.color_map3:
        xmlfile.write('<map type="color">%s</map>\n' % (bulletin.color_map3))


def write_bulletin_xml_file(bulletin, basedir):
    latex_output_dir = basedir + '/output'
    if not os.path.isdir(latex_output_dir):
        os.makedirs(latex_output_dir)

    filename = '%s/output/bulletin_%s.xml' % (basedir, bulletin.id)
    xmlfile = open(filename, 'w')

    bulletin_gis_hash = get_all_regions_gis_hash(bulletin.id)

    xmlfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    xmlfile.write('<regions name="%s" editors="%s" file_prefix="bulletin_%s" all_regions_gis_hash="%s">\n' % \
                  (bulletin.bulletin_name, bulletin.editors, bulletin.id, bulletin_gis_hash))

    indexed_terms = get_indexed_terms(bulletin)

    xmlfile.write('<indexed_terms>\n')
    for term in indexed_terms[0]:
        xmlfile.write('<term search="%s" index="%s"/>\n' % (term, indexed_terms[1][term]))
    xmlfile.write('</indexed_terms>\n')

    xmlfile.write('<maps>\n')
    for gismap in cavedb.models.GisMap.objects.all():
        xmlfile.write('<map name="%s" description="%s" website_url="%s" license_url="%s" map_label="%s"/>\n' % \
                      (convert_quotes(gismap.name), convert_quotes(gismap.description), \
                       convert_quotes(gismap.website_url), convert_quotes(gismap.license_url), \
                       convert_quotes(gismap.map_label)))
    xmlfile.write('</maps>\n')

    write_bulletin_maps(xmlfile, bulletin)

    write_gis_section(xmlfile, bulletin.id)

    xmlfile.write('<title_page>%s</title_page>\n' % \
            (generate_index(convert_quotes(bulletin.title_page), indexed_terms)))

    xmlfile.write('<preamble_page>%s</preamble_page>\n' % \
            (generate_index(convert_quotes(bulletin.preamble_page), indexed_terms)))

    if bulletin.contributor_page:
        xmlfile.write('<contributor_page>%s</contributor_page>\n' % \
                (generate_index(convert_quotes(bulletin.contributor_page), indexed_terms)))

    if bulletin.toc_footer:
        xmlfile.write('<toc_footer>%s</toc_footer>\n' % \
                (generate_index(convert_quotes(bulletin.toc_footer), indexed_terms)))

    if bulletin.caves_header:
        xmlfile.write('<caves_header>%s</caves_header>\n' % \
                (generate_index(convert_quotes(bulletin.caves_header), indexed_terms)))

    if bulletin.photo_index_header:
        xmlfile.write('<photo_index_header>%s</photo_index_header>\n' % \
                (convert_quotes(bulletin.photo_index_header)))

    if bulletin.dvd_readme:
        xmlfile.write('<dvd_readme>%s</dvd_readme>\n' % (escape(bulletin.dvd_readme)))

    write_chapters(xmlfile, bulletin, indexed_terms)

    for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        map_name = region.map_region_name
        if not map_name:
            map_name = region.region_name

        gis_region_hash = get_region_gis_hash(region.id)

        xmlfile.write('<region name="%s" map_name="%s" file_prefix="bulletin_%s_region_%s" show_gis_map="%s" gis_hash="%s">\n' % \
                      (region.region_name, map_name, bulletin.id, region.id, int(region.show_gis_map), gis_region_hash))
        if region.introduction:
            xmlfile.write('<introduction>%s</introduction>' % \
                    (generate_index(convert_quotes(region.introduction), indexed_terms)))

        xmlfile.write('<features>\n')

        for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
            write_feature(xmlfile, feature, indexed_terms)

        xmlfile.write('</features>\n')
        xmlfile.write('</region>\n')

    write_all_references(xmlfile, bulletin)

    write_feature_indexes(xmlfile, bulletin)

    xmlfile.write('</regions>\n')

    xmlfile.close()


def write_makefile(bulletin_id, basedir):
    filename = '%s/Makefile' % (basedir)
    xmlfile = open(filename, 'w')

    xmlfile.write('DOCPREFIX=bulletin_%s\n' % (bulletin_id))
    xmlfile.write('DOC_BASE_DIR=$(shell pwd)\n')
    xmlfile.write('OUTPUTDIR=$(DOC_BASE_DIR)/output\n')
    xmlfile.write('TEMPLATE_BASE_DIR=$(DOC_BASE_DIR)/../base_bulletin\n')
    xmlfile.write('include $(TEMPLATE_BASE_DIR)/Makefile.include\n')

    xmlfile.close()


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
    xmlfile = open(filename, 'w')

    # This lockfile is checked by the web interface to see if a build is
    # in progress.

    xmlfile.write('#!/bin/bash\n')
    xmlfile.write('touch build-in-progress.lock\n')
    xmlfile.write('make\n')
    xmlfile.write('rm -f build-in-progress.lock\n')

    xmlfile.close()
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


def add_gis_lineplot(xmlfile, lineplot, gisdir, lineplot_type):
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

    xmlfile.write('<lineplot>\n<id>%s</id>\n<type>%s</type>\n<file>%s/%s</file>\n<description>%s</description>\n<datum>%s</datum>\n<coord_sys>%s</coord_sys>\n</lineplot>\n' % \
                  (lineplot.id, lineplot_type, gisdir, lineplot.shp_filename, \
                   lineplot.description, lineplot.datum, lineplot.coord_sys))


def expand_gis_lineplots(xmlfile, bulletin_id):
    # Expand cave and surface lineplots
    for lineplot in cavedb.models.BulletinGisLineplot.objects.filter(bulletin__id=bulletin_id):
        gisdir = '%s/bulletins/bulletin_%s/output/lineplots/bulletin_lineplot_%s' % \
                 (settings.MEDIA_ROOT, lineplot.bulletin.id, lineplot.id)
        add_gis_lineplot(xmlfile, lineplot, gisdir, 'surface')


    for lineplot in cavedb.models.FeatureGisLineplot.objects.filter(feature__bulletin_region__bulletin__id=bulletin_id):
        gisdir = '%s/bulletins/bulletin_%s/output/lineplots/feature_lineplot_%s' % \
                 (settings.MEDIA_ROOT, lineplot.feature.bulletin_region.bulletin.id, lineplot.id)
        add_gis_lineplot(xmlfile, lineplot, gisdir, 'underground')


def write_gis_section(xmlfile, bulletin_id):
    legend_titles = {}

    xmlfile.write('<gis_layers>\n')

    for layer in cavedb.models.GisLayer.objects.all():
        xmlfile.write('<gis_layer>\n')
        xmlfile.write('<name>%s</name>\n' % (layer.table_name))

        for gismap in layer.maps.all():
            xmlfile.write('<map_name>%s</map_name>\n' % (gismap.name))

        xmlfile.write('<connection_type>%s</connection_type>\n' % (settings.GIS_CONNECTION_TYPE))
        xmlfile.write('<connection>%s</connection>\n' % (settings.GIS_CONNECTION))

        if layer.filename:
            xmlfile.write('<data>%s</data>\n' % (layer.filename))
        else:
            xmlfile.write('<data>geom from %s</data>\n' % (layer.table_name))

        xmlfile.write('<display>%s</display>\n' % (int(layer.display)))
        xmlfile.write('<type>%s</type>\n' % (layer.type))

        if layer.label_item:
            xmlfile.write('<label_item>%s</label_item>\n' % (layer.label_item))

        if layer.description:
            if layer.description not in legend_titles:
                legend_titles[layer.description] = 1
                xmlfile.write('<legend first_occurance="1">%s</legend>\n' % (layer.description))
            else:
                xmlfile.write('<legend first_occurance="0">%s</legend>\n' % (layer.description))

        colors = layer.color.split(' ')
        if len(colors) > 2:
            xmlfile.write('<color red="%s" green="%s" blue="%s"/>\n' % \
                          (colors[0], colors[1], colors[2]))

        if layer.symbol:
            xmlfile.write('<symbol>%s</symbol>\n' % (layer.symbol))
            xmlfile.write('<symbol_size>%s</symbol_size>\n' % (layer.symbol_size))
        elif layer.symbol_size:
            xmlfile.write('<symbol></symbol>\n')
            xmlfile.write('<symbol_size>%s</symbol_size>\n' % (layer.symbol_size))

        if layer.line_type:
            xmlfile.write('<line_type>%s</line_type>\n' % (layer.line_type))

        if layer.max_scale:
            xmlfile.write('<max_scale>%s</max_scale>\n' % (layer.max_scale))

        if layer.label_item:
            colors = layer.font_color.split(' ')
            xmlfile.write('<font_color red="%s" green="%s" blue="%s"/>\n' % \
                    (colors[0], colors[1], colors[2]))
            xmlfile.write('<font_size>%s</font_size>\n' % (layer.font_size))

        xmlfile.write('</gis_layer>\n')

    expand_gis_lineplots(xmlfile, bulletin_id)

    xmlfile.write('</gis_layers>\n')


def generate_bulletin(request, bulletin_id):
    if not cavedb.utils.is_bulletin_generation_allowed(bulletin_id):
        raise Http404

    bulletins = cavedb.models.Bulletin.objects.filter(id=bulletin_id)
    if bulletins.count() == 0:
        raise Http404

    bulletin = bulletins[0]
    basedir = '%s/bulletins/bulletin_%s' % (settings.MEDIA_ROOT, bulletin_id)

    write_bulletin_xml_file(bulletin, basedir)
    write_makefile(bulletin_id, basedir)
    write_buildscript(basedir)
    run_make_command(basedir)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))


def generate_xml_only_bulletin(request, bulletin_id):
    if not cavedb.utils.is_bulletin_generation_allowed(bulletin_id):
        raise Http404

    bulletins = cavedb.models.Bulletin.objects.filter(id=bulletin_id)
    if bulletins.count() == 0:
        raise Http404

    bulletin = bulletins[0]
    basedir = '%s/bulletins/bulletin_%s' % (settings.MEDIA_ROOT, bulletin_id)

    write_bulletin_xml_file(bulletin, basedir)
    write_makefile(bulletin_id, basedir)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))

def generate_all_xml_only_bulletin(request):
    for bulletin in cavedb.models.Bulletin.objects.all():
        if not cavedb.utils.is_bulletin_generation_allowed(bulletin.id):
            continue

        generate_xml_only_bulletin(request, bulletin.id)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))

