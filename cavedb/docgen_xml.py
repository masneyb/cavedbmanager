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

import re
from xml.sax.saxutils import escape
import datetime
import dateutil.parser
import dateutil.relativedelta
from django.conf import settings
import cavedb.models
import cavedb.utils
import cavedb.docgen_common

class Xml(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)
        self.legend_titles = {}
        self.indexed_terms = None
        self.num_in_pdf = 1
        self.xmlfile = None


    def open(self, all_regions_gis_hash):
        self.create_directory('/output')
        filename = '%s/output/bulletin_%s.xml' % (self.basedir, self.bulletin.id)
        self.xmlfile = open(filename, 'w')

        self.xmlfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.xmlfile.write('<regions name="%s" editors="%s" file_prefix="bulletin_%s" all_regions_gis_hash="%s">\n' % \
                           (self.bulletin.bulletin_name, self.bulletin.editors, self.bulletin.id,
                            all_regions_gis_hash))

        self.indexed_terms = self.get_indexed_terms()

        self.xmlfile.write('<indexed_terms>\n')
        for term in self.indexed_terms[0]:
            self.xmlfile.write('<term search="%s" index="%s"/>\n' % \
                               (term, self.indexed_terms[1][term]))
        self.xmlfile.write('</indexed_terms>\n')

        self.xmlfile.write('<title_page>%s</title_page>\n' % \
                           (self.generate_index(convert_quotes(self.bulletin.title_page))))

        self.xmlfile.write('<preamble_page>%s</preamble_page>\n' % \
                           (self.generate_index(convert_quotes(self.bulletin.preamble_page))))

        if self.bulletin.contributor_page:
            self.xmlfile.write('<contributor_page>%s</contributor_page>\n' % \
                               (self.generate_index(convert_quotes(self.bulletin.contributor_page))))

        if self.bulletin.toc_footer:
            self.xmlfile.write('<toc_footer>%s</toc_footer>\n' % \
                               (self.generate_index(convert_quotes(self.bulletin.toc_footer))))

        if self.bulletin.caves_header:
            self.xmlfile.write('<caves_header>%s</caves_header>\n' % \
                               (self.generate_index(convert_quotes(self.bulletin.caves_header))))

        if self.bulletin.photo_index_header:
            self.xmlfile.write('<photo_index_header>%s</photo_index_header>\n' % \
                               (convert_quotes(self.bulletin.photo_index_header)))

        if self.bulletin.dvd_readme:
            self.xmlfile.write('<dvd_readme>%s</dvd_readme>\n' % (escape(self.bulletin.dvd_readme)))

        self.write_chapters()


    def begin_gis_maps(self):
        if self.bulletin.bw_map1:
            self.xmlfile.write('<map type="black_and_white">%s</map>\n' % (self.bulletin.bw_map1))
        if self.bulletin.bw_map2:
            self.xmlfile.write('<map type="black_and_white">%s</map>\n' % (self.bulletin.bw_map2))
        if self.bulletin.bw_map3:
            self.xmlfile.write('<map type="black_and_white">%s</map>\n' % (self.bulletin.bw_map3))
        if self.bulletin.color_map1:
            self.xmlfile.write('<map type="color">%s</map>\n' % (self.bulletin.color_map1))
        if self.bulletin.color_map2:
            self.xmlfile.write('<map type="color">%s</map>\n' % (self.bulletin.color_map2))
        if self.bulletin.color_map3:
            self.xmlfile.write('<map type="color">%s</map>\n' % (self.bulletin.color_map3))

        self.xmlfile.write('<maps>\n')


    def gis_map(self, gismap):
        self.xmlfile.write('<map name="%s" description="%s" website_url="%s" license_url="%s" map_label="%s"/>\n' % \
                           (convert_quotes(gismap.name), convert_quotes(gismap.description), \
                            convert_quotes(gismap.website_url), \
                            convert_quotes(gismap.license_url), \
                            convert_quotes(gismap.map_label)))


    def end_gis_maps(self):
        self.xmlfile.write('</maps>\n')


    def gis_lineplot(self, lineplot, lineplot_type, shpfilename):
        self.xmlfile.write('<lineplot>\n<id>%s</id>\n<type>%s</type>\n<file>%s</file>\n<description>%s</description>\n<datum>%s</datum>\n<coord_sys>%s</coord_sys>\n</lineplot>\n' % \
                           (lineplot.id, lineplot_type, shpfilename, lineplot.description, \
                            lineplot.datum, lineplot.coord_sys))


    def begin_gis_layers(self):
        self.xmlfile.write('<gis_layers>\n')


    def gis_layer(self, layer):
        self.xmlfile.write('<gis_layer>\n')
        self.xmlfile.write('<name>%s</name>\n' % (layer.table_name))

        for gismap in layer.maps.all():
            self.xmlfile.write('<map_name>%s</map_name>\n' % (gismap.name))

        self.xmlfile.write('<connection_type>%s</connection_type>\n' % \
                           (settings.GIS_CONNECTION_TYPE))
        self.xmlfile.write('<connection>%s</connection>\n' % (settings.GIS_CONNECTION))

        if layer.filename:
            self.xmlfile.write('<data>%s</data>\n' % (layer.filename))
        else:
            self.xmlfile.write('<data>geom from %s</data>\n' % (layer.table_name))

        self.xmlfile.write('<display>%s</display>\n' % (int(layer.display)))
        self.xmlfile.write('<type>%s</type>\n' % (layer.type))

        if layer.label_item:
            self.xmlfile.write('<label_item>%s</label_item>\n' % (layer.label_item))

        if layer.description:
            if layer.description not in self.legend_titles:
                self.legend_titles[layer.description] = 1
                self.xmlfile.write('<legend first_occurance="1">%s</legend>\n' % \
                                   (layer.description))
            else:
                self.xmlfile.write('<legend first_occurance="0">%s</legend>\n' % \
                                   (layer.description))

        colors = layer.color.split(' ')
        if len(colors) > 2:
            self.xmlfile.write('<color red="%s" green="%s" blue="%s"/>\n' % \
                          (colors[0], colors[1], colors[2]))

        if layer.symbol:
            self.xmlfile.write('<symbol>%s</symbol>\n' % (layer.symbol))
            self.xmlfile.write('<symbol_size>%s</symbol_size>\n' % (layer.symbol_size))
        elif layer.symbol_size:
            self.xmlfile.write('<symbol></symbol>\n')
            self.xmlfile.write('<symbol_size>%s</symbol_size>\n' % (layer.symbol_size))

        if layer.line_type:
            self.xmlfile.write('<line_type>%s</line_type>\n' % (layer.line_type))

        if layer.max_scale:
            self.xmlfile.write('<max_scale>%s</max_scale>\n' % (layer.max_scale))

        if layer.label_item:
            colors = layer.font_color.split(' ')
            self.xmlfile.write('<font_color red="%s" green="%s" blue="%s"/>\n' % \
                    (colors[0], colors[1], colors[2]))
            self.xmlfile.write('<font_size>%s</font_size>\n' % (layer.font_size))

        self.xmlfile.write('</gis_layer>\n')


    def end_gis_layers(self):
        self.xmlfile.write('</gis_layers>\n')


    def begin_region(self, region, gis_region_hash, map_name):
        self.xmlfile.write('<region name="%s" map_name="%s" file_prefix="bulletin_%s_region_%s" show_gis_map="%s" gis_hash="%s">\n' % \
                           (region.region_name, map_name, self.bulletin.id, region.id,
                            int(region.show_gis_map), gis_region_hash))
        if region.introduction:
            self.xmlfile.write('<introduction>%s</introduction>' % \
                               (self.generate_index(convert_quotes(region.introduction))))

        self.xmlfile.write('<features>\n')


    def end_region(self):
        self.xmlfile.write('</features>\n')
        self.xmlfile.write('</region>\n')


    def begin_feature(self, feature):
        self.num_in_pdf = 1

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

        self.xmlfile.write('<feature %s>\n' % (feature_att_str))

        self.xmlfile.write('<name>%s</name>\n' % (feature.name.strip()))

        if feature.alternate_names:
            for alias in feature.alternate_names.split(','):
                alias = alias.strip()
                if alias:
                    self.xmlfile.write('<aliases>%s</aliases>\n' % (alias))

        if feature.additional_index_names:
            for alias in feature.additional_index_names.split(','):
                alias = alias.strip()
                if alias:
                    self.xmlfile.write('<additional_index_name>%s</additional_index_name>\n' % \
                                       (alias))

        if feature.length_ft:
            self.xmlfile.write('<length>%s</length>\n' % (feature.length_ft))

        if feature.depth_ft:
            self.xmlfile.write('<depth>%s</depth>\n' % (feature.depth_ft))

        if feature.length_based_on:
            self.xmlfile.write('<length_based_on>%s</length_based_on>\n' % \
                               (feature.length_based_on))

        if feature.description:
            if feature.source:
                self.xmlfile.write('<desc author="%s">%s</desc>\n' % \
                                   (convert_quotes(feature.source), \
                                    self.generate_index(convert_nl_to_para(feature.description))))
            else:
                self.xmlfile.write('<desc>%s</desc>\n' % \
                                   (self.generate_index(convert_nl_to_para(feature.description))))

        if feature.history:
            self.xmlfile.write('<history>%s</history>\n' % \
                               (self.generate_index(convert_quotes(feature.history))))

        if feature.internal_history:
            self.xmlfile.write('<internal_history>%s</internal_history>\n' % \
                               (self.generate_index(convert_quotes(feature.internal_history))))

        if feature.biology:
            self.xmlfile.write('<biology>%s</biology>\n' % \
                               (self.generate_index(convert_quotes(feature.biology))))

        if feature.geology_hydrology:
            self.xmlfile.write('<geology>%s</geology>\n' % \
                               (self.generate_index(convert_quotes(feature.geology_hydrology))))

        if feature.hazards:
            self.xmlfile.write('<hazards>%s</hazards>\n' % \
                               (self.generate_index(convert_quotes(feature.hazards))))

        if feature.owner_name:
            self.xmlfile.write('<owner_name>%s</owner_name>\n' % (feature.owner_name))

        if feature.owner_address:
            self.xmlfile.write('<owner_address>%s</owner_address>\n' % (feature.owner_address))

        if feature.owner_phone:
            self.xmlfile.write('<owner_phone>%s</owner_phone>\n' % (feature.owner_phone))

        if feature.access_enum and feature.access_descr:
            self.xmlfile.write('<access status="%s">%s</access>\n' % \
                               (feature.access_enum, feature.access_descr))


    def feature_todo(self, todo_enum, todo_descr):
        self.xmlfile.write('<bulletin_work category="%s">%s</bulletin_work>\n' % \
                           (todo_enum, todo_descr))


    def feature_entrance(self, feature, ent, utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, \
                         wgs84_lon):
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

            self.xmlfile.write('<location%s id="%s" wgs84_lat="%s" wgs84_lon="%s" utmzone="%s" utm27_utmeast="%s" utm27_utmnorth="%s" ele="%s" county="%s" quad="%s"/>\n' % \
                               (attstr, ent.id, wgs84_lat, wgs84_lon, utmzone, nad27_utmeast, \
                                nad27_utmnorth, ent.elevation_ft, ent.county, quad_name))


    def feature_attachment(self, feature, attachment):
        attrs = 'filename="%s" type="%s"' % (attachment.attachment, attachment.attachment_type)
        if attachment.description:
            attrs += ' description="%s"' % (convert_quotes(attachment.description))
        if attachment.user_visible_file_suffix:
            attrs += ' user_visible_file_suffix="%s"' % \
                     (convert_quotes(attachment.user_visible_file_suffix))
        if attachment.author:
            attrs += ' author="%s"' % (convert_quotes(attachment.author))

        self.xmlfile.write('<attachment %s/>\n' % (attrs))


    def feature_photo(self, feature, photo):
        attrs = 'id="photo%s" type="%s" scale="%s" rotate="%s" base_directory="%s" primary_filename="%s" secondary_filename="%s" sort_order="%s" show_at_end="%s" include_on_dvd="%s" show_in_pdf="%s"' % \
                (photo.id, photo.type, photo.scale, photo.rotate_degrees, settings.MEDIA_ROOT, \
                 photo.filename, photo.secondary_filename, photo.sort_order, \
                 int(photo.show_at_end), int(photo.include_on_dvd), int(photo.show_in_pdf))

        if photo.show_in_pdf:
            attrs += ' num_in_pdf="%s"' % (self.num_in_pdf)
            self.num_in_pdf = self.num_in_pdf + 1
        if photo.caption:
            attrs += ' caption="%s"' % (format_photo_caption(feature, photo.caption))
        if photo.people_shown:
            attrs += ' people_shown="%s"' % (convert_quotes(photo.people_shown))
        if photo.author:
            attrs += ' author="%s"' % (convert_quotes(photo.author))

        self.xmlfile.write('<photo %s>\n' % (attrs))

        if photo.indexed_terms:
            for term in photo.indexed_terms.split('\n'):
                self.xmlfile.write('<index>%s</index>\n' % (term.strip()))

        self.xmlfile.write('</photo>\n')


    def feature_referenced_map(self, feature, refmap):
        self.xmlfile.write('<photo ref="photo%s" type="map" show_in_pdf="1" />\n' % (refmap.map.id))


    def feature_reference(self, feature, ref):
        self.write_reference(ref)


    def end_feature(self):
        self.xmlfile.write('</feature>\n')


    def close(self):
        self.write_feature_indexes()
        self.write_all_references()
        self.xmlfile.write('</regions>\n')
        self.xmlfile.close()


    def get_indexed_terms(self):
        indexed_terms = [], {}
        if self.bulletin.indexed_terms:
            for search_term in self.bulletin.indexed_terms.split('\n'):
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
                    indexed_terms[1][all_index_terms[0]] = '%s%s' % \
                       (replacement, all_index_terms[0])

        for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=self.bulletin.id):
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


    def clean_index(self, inputstr):
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
            return '%s%s%s%s' % (result.group(1), result.group(2), value, \
                                 self.clean_index(result.group(4)))
        elif not re.compile(r'^.*\\caveindex.*$', flags).match(result.group(3)):
            if re.compile(r'^.*\\caveindex.*$', flags).match(result.group(4)):
                return '%s%s%s}%s' % (result.group(1), result.group(2), result.group(3), \
                                      self.clean_index(result.group(4)))
            else:
                return inputstr
        else:
            value = re.sub(r'^(.*?)\s\\caveindex{(.*)', r'\1 \2', result.group(3))
            return '%s%s' % (result.group(1),
                             self.clean_index('%s%s%s' % (result.group(2), value, result.group(4))))


    def finalize_index(self, inputstr):
        flags = re.MULTILINE | re.DOTALL | re.VERBOSE
        result = re.compile(r'(.*?)\\caveindex{(.*?)}(.*)', flags).match(inputstr)
        if not result:
            return inputstr

        return '%s%s%s' % (result.group(1), self.indexed_terms[1][result.group(2)], \
                           self.finalize_index(result.group(3)))


    def generate_index(self, inputstr):
        # Add terms to the index
        for term in self.indexed_terms[0]:
            # This appears to be quicker than doing a single regular expression
            inputstr = inputstr.replace('%s ' % (term), r'\caveindex{%s} ' % (term))
            inputstr = inputstr.replace('%s.' % (term), r'\caveindex{%s}.' % (term))
            inputstr = inputstr.replace('%s,' % (term), r'\caveindex{%s},' % (term))
            inputstr = inputstr.replace('%s:' % (term), r'\caveindex{%s}:' % (term))
            inputstr = inputstr.replace('%s)' % (term), r'\caveindex{%s})' % (term))
            inputstr = inputstr.replace('%s\'' % (term), r'\caveindex{%s}\'' % (term))

        return self.finalize_index(self.clean_index(inputstr))


    def write_chapters(self):
        self.xmlfile.write('<chapters>\n')

        for chapter in cavedb.models.BulletinChapter.objects.filter(bulletin__id=self.bulletin.id):
            self.xmlfile.write('<chapter title="%s" is_appendix="%i">\n' % \
                    (chapter.chapter_title, chapter.is_appendix))

            for section in cavedb.models.BulletinSection.objects \
               .filter(bulletin_chapter__id=chapter.id):

                section_attrs = ''
                if section.section_title:
                    section_attrs = '%s title="%s"' % (section_attrs, section.section_title)

                if section.section_subtitle:
                    section_attrs = '%s subtitle="%s"' % (section_attrs, section.section_subtitle)

                self.xmlfile.write('<section%s>\n' % (section_attrs))
                self.xmlfile.write('<text num_columns="%s">%s</text>' % \
                        (section.num_columns, \
                         self.generate_index(convert_quotes(section.section_data))))

                for ref in cavedb.models.BulletinSectionReference.objects \
                   .filter(bulletinsection__id=section.id):

                    self.write_reference(ref)

                self.xmlfile.write('</section>\n')

            self.xmlfile.write('</chapter>')

        self.xmlfile.write('</chapters>\n')


    def write_feature_indexes(self):
        aliases = {}

        # Show all of the names and aliases in one place so that they can be sorted in the index
        self.xmlfile.write('<feature_indexes>\n')

        for feature in cavedb.models.Feature.objects \
           .filter(bulletin_region__bulletin__id=self.bulletin.id):

            self.xmlfile.write('<index name="%s" is_primary="1"/>\n' % (feature.name.strip()))

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
            self.xmlfile.write('<index name="%s" is_alias="1">\n' % (alias))
            for feature_id in aliases[alias]:
                self.xmlfile.write('<feature_id>%s</feature_id>\n' % (feature_id))

            self.xmlfile.write('</index>\n')

        self.xmlfile.write('</feature_indexes>\n')


    def write_all_references(self):
        # Write out all references together for the bibliography
        self.xmlfile.write('<all_references>\n')

        for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=self.bulletin.id):
            for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
                for ref in cavedb.models.FeatureReference.objects.filter(feature=feature.id):
                    self.write_reference(ref)

        for chapter in cavedb.models.BulletinChapter.objects.filter(bulletin__id=self.bulletin.id):
            for section in cavedb.models.BulletinSection.objects \
               .filter(bulletin_chapter__id=chapter.id):

                for ref in cavedb.models.BulletinSectionReference.objects \
                   .filter(bulletinsection__id=section.id):

                    self.write_reference(ref)

        self.xmlfile.write('</all_references>\n')


    def write_reference(self, ref):
        hidden_in_bibliography = ref.title.startswith('unpublished trip report') or \
                                 ref.title.startswith('Tucker County Speleological Survey Files') or \
                                 ref.title.startswith('personal communication') or \
                                 ref.title.startswith('e-mail') or \
                                 ref.title.startswith('letter to') or \
                                 ref.title.startswith('Trip Report in NSS Files')

        self.xmlfile.write('<reference author="%s" title="%s" book="%s" volume="%s" number="%s" pages="%s" url="%s" date="%s" extra="%s" parsed_date="%s" hidden_in_bibliography="%s"/>\n' % \
                           (convert_quotes(ref.author), convert_quotes(ref.title), \
                            convert_quotes(ref.book), convert_quotes(ref.volume), \
                            convert_quotes(ref.number), convert_quotes(ref.pages), \
                            convert_quotes(ref.url), convert_quotes(ref.date),
                            convert_quotes(ref.extra), \
                            get_normalized_date(ref.date), hidden_in_bibliography))


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

