# SPDX-License-Identifier: Apache-2.0

import cavedb.utils
import cavedb.docgen_common

class Text(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self)
        self.bulletin = bulletin
        self.textfile = None


    def open(self, all_regions_gis_hash):
        # pylint: disable=consider-using-with
        filename = get_text_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.textfile = open(filename, 'w', encoding='utf-8')

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


    def begin_regions(self, chapters):
        self.write_chapters(chapters)


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


    def write_chapters(self, chapters):
        for chapter_and_sections in chapters:
            chapter = chapter_and_sections['chapter']

            self.textfile.write('%s\n\n' % (chapter.chapter_title))

            for section, refs in chapter_and_sections['sections_and_refs']:
                self.textfile.write('%s\n\n' % (section.section_title))

                if section.section_subtitle:
                    self.textfile.write('%s\n\n' % (section.section_subtitle))

                self.textfile.write('%s\n\n' % (section.section_data))

                for ref in refs:
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
