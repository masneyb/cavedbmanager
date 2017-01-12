# Copyright 2016-2017 Brian Masney <masneyb@onstation.org>
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

import cavedb.models
import cavedb.utils
import cavedb.docgen_common

class Text(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self)
        self.bulletin = bulletin
        self.textfile = None


    def open(self, all_regions_gis_hash):
        filename = get_text_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.textfile = open(filename, 'w')

        if self.bulletin.title_page:
            self.textfile.write('%s\n\n' % (self.bulletin.title_page))

        if self.bulletin.preamble_page:
            self.textfile.write('%s\n\n' % (self.bulletin.preamble_page))

        if self.bulletin.contributor_page:
            self.textfile.write('%s\n\n' % (self.bulletin.contributor_page))

        if self.bulletin.toc_footer:
            self.textfile.write('%s\n\n' % (self.bulletin.toc_footer))

        if self.bulletin.caves_header:
            self.textfile.write('%s\n\n' % (self.bulletin.caves_header))

        if self.bulletin.photo_index_header:
            self.textfile.write('%s\n\n' % (self.bulletin.photo_index_header))

        self.write_chapters()


    def begin_region(self, region, gis_region_hash):
        self.textfile.write('%s\n\n' % (region.region_name))

        if region.introduction:
            self.textfile.write('%s\n\n' % (region.introduction))


    def end_region(self):
        self.textfile.write('\n\n')


    def begin_feature(self, feature):
        self.textfile.write('%s\n' % (feature.name.strip()))

        if feature.alternate_names:
            for alias in feature.alternate_names.split(','):
                alias = alias.strip()
                if alias:
                    self.textfile.write('%s\n' % (alias))

        if feature.hazards:
            self.textfile.write('%s\n\n' % (feature.hazards))

        if feature.description:
            self.textfile.write('%s\n\n' % (feature.description))

        if feature.history:
            self.textfile.write('%s\n\n' % (feature.history))

        if feature.biology:
            self.textfile.write('%s\n\n' % (feature.biology))

        if feature.geology_hydrology:
            self.textfile.write('%s\n\n' % (feature.geology_hydrology))


    def feature_reference(self, feature, ref):
        self.write_reference(ref)


    def end_feature(self):
        self.textfile.write('\n\n')


    def close(self):
        self.textfile.close()


    def write_chapters(self):
        for chapter in cavedb.models.BulletinChapter.objects.filter(bulletin__id=self.bulletin.id):
            self.textfile.write('%s\n\n' % (chapter.chapter_title))

            for section in cavedb.models.BulletinSection.objects \
               .filter(bulletin_chapter__id=chapter.id):

                self.textfile.write('%s\n\n' % (section.section_title))

                if section.section_subtitle:
                    self.textfile.write('%s\n\n' % (section.section_subtitle))

                self.textfile.write('%s\n\n' % (section.section_data))

                for ref in cavedb.models.BulletinSectionReference.objects \
                   .filter(bulletinsection__id=section.id):

                    self.write_reference(ref)


    def write_reference(self, ref):
        self.textfile.write('%s, %s, %s, V%sN%sP%s,%s,%s,%s\n' % \
                            (ref.author, ref.title, ref.book, ref.volume, ref.number, ref.pages, \
                             ref.url, ref.date, ref.extra))


    def create_html_download_urls(self):
        return self.create_url('bulletin/%s/text' % \
                               (self.bulletin.id), 'Text (TXT)', \
                                get_text_filename(self.bulletin.id))


def get_text_filename(bulletin_id):
    return '%s/text/bulletin_%s.txt' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
