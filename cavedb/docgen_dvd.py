# Copyright 2016 Brian Masney <masneyb@onstation.org>
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
import cavedb.docgen_common
import cavedb.utils
import cavedb.settings

class Dvd(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self, bulletin)
        self.files = {}
        self.files['include_on_dvd'] = {}
        self.files['exclude_from_dvd'] = {}

        # Tuple contains (Directory Name, File Suffix)
        self.phototypes = {}
        self.phototypes['map'] = ('Maps', 'Map')
        self.phototypes['entrance_picture'] = ('Entrance Photos', 'Entrance Photo')
        self.phototypes['in_cave_picture'] = ('In Cave Photos', 'In Cave Photo')
        self.phototypes['surface_picture'] = ('Surface Photos', 'Surface Photo')
        self.phototypes['drawing'] = ('Drawings', 'Drawing')
        self.phototypes['other'] = ('Others', 'Other')
        self.phototypes['attachment'] = ('Attachments', 'Attachment')


    def feature_photo(self, feature, photo):
        if not photo.include_on_dvd:
            return

        meta = {}
        meta['src'] = '%s/%s' % (cavedb.settings.MEDIA_ROOT, photo.filename)
        if photo.author:
            meta['author'] = photo.author

        toplevel_dir = 'include_on_dvd' if photo.include_on_dvd else 'exclude_from_dvd'
        self.__add_meta(toplevel_dir, photo.type, feature.name, meta)


    def feature_attachment(self, feature, attachment):
        meta = {}
        meta['src'] = '%s/%s' % (cavedb.settings.MEDIA_ROOT, attachment.attachment)
        if attachment.author:
            meta['author'] = attachment.author
        if attachment.user_visible_file_suffix:
            meta['user_visible_file_suffix'] = attachment.user_visible_file_suffix

        self.__add_meta('exclude_from_dvd', 'attachment', feature.name, meta)


    def __add_meta(self, toplevel_dir, photo_type, feature_name, meta):
        if photo_type not in self.files[toplevel_dir]:
            self.files[toplevel_dir][photo_type] = {}

        if feature_name not in self.files[toplevel_dir][photo_type]:
            self.files[toplevel_dir][photo_type][feature_name] = []

        self.files[toplevel_dir][photo_type][feature_name].append(meta)


    def generate_buildscript(self):
        output_base_dir = cavedb.utils.get_output_base_dir(self.bulletin.id)
        dvd_tmp_dir = '%s/dvd' % (output_base_dir)

        ret = 'rm -rf "%s/"\n' % (dvd_tmp_dir)
        ret += 'mkdir -p "%s"\n' % (dvd_tmp_dir)

        if self.bulletin.dvd_readme:
            readme_file = '%s/README.txt' % (cavedb.utils.get_output_base_dir(self.bulletin.id))
            with open(readme_file, 'w') as output:
                output.write(self.bulletin.dvd_readme)

            ret += 'mv "%s" "%s/"\n' % (readme_file, dvd_tmp_dir)

        for toplevel_dir in self.files.keys():
            for photo_type in self.files[toplevel_dir].keys():
                dvd_dir = '%s/%s/%s' % (dvd_tmp_dir, toplevel_dir, self.phototypes[photo_type][0])
                ret += 'mkdir -p "%s"\n' % (dvd_dir)

                for feature_name in self.files[toplevel_dir][photo_type].keys():
                    num_photos = len(self.files[toplevel_dir][photo_type][feature_name])
                    photo_num = 1

                    for photo_meta in self.files[toplevel_dir][photo_type][feature_name]:
                        destfile = '%s/%s %s' % \
                                   (dvd_dir, feature_name, self.phototypes[photo_type][1])

                        if num_photos > 1:
                            destfile += ' - %02d of %02d' % (photo_num, num_photos)
                            photo_num = photo_num + 1

                        if 'author' in photo_meta:
                            destfile += ' - %s' % (photo_meta['author'])

                        extpos = photo_meta['src'].rfind('.')
                        destfile += photo_meta['src'][extpos:]

                        ret += 'ln "%s" "%s"\n' % (photo_meta['src'], destfile)

        dvd_zip_file = get_dvd_filename(self.bulletin.id)
        ret += 'cd %s\n' % (output_base_dir)
        ret += 'rm -f "%s"\n' % (dvd_zip_file)
        ret += 'zip -r "%s" "%s"\n' % (dvd_zip_file, os.path.basename(dvd_tmp_dir))
        ret += 'rm -rf "%s/"\n' % (dvd_tmp_dir)

        return ret


    def create_html_download_urls(self):
        return self.create_url('/dvd', 'Supplemental DVD (ZIP)', get_dvd_filename(self.bulletin.id))


def get_dvd_filename(bulletin_id):
    return '%s/dvd.zip' % (cavedb.utils.get_output_base_dir(bulletin_id))
