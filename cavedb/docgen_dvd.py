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

import os
import cavedb.docgen_common
import cavedb.utils
import cavedb.settings

class Dvd(cavedb.docgen_common.Common):
    def __init__(self, dvd_zip_file, dvd_tmp_dir, readme_contents, download_url):
        cavedb.docgen_common.Common.__init__(self)
        self.dvd_zip_file = dvd_zip_file
        self.dvd_tmp_dir = dvd_tmp_dir
        self.readme_contents = readme_contents
        self.download_url = download_url

        self.files = {}
        self.files['include_on_dvd'] = {}
        self.files['exclude_from_dvd'] = {}

        # Tuple contains (Directory Name, File Suffix)
        self.phototypes = {}
        self.phototypes['map'] = ('Maps', 'Map')
        self.phototypes['entrance_picture'] = ('EntrancePhotos', 'Entrance Photo')
        self.phototypes['in_cave_picture'] = ('InCavePhotos', 'In Cave Photo')
        self.phototypes['surface_picture'] = ('SurfacePhotos', 'Surface Photo')
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
        ret = 'rm -rf "%s/"\n' % (self.dvd_tmp_dir)
        ret += 'mkdir -p "%s"\n' % (self.dvd_tmp_dir)

        output_base_dir = os.path.dirname(self.dvd_tmp_dir)

        if self.readme_contents:
            readme_file = '%s/README.txt' % (output_base_dir)
            with open(readme_file, 'w') as output:
                output.write(self.readme_contents)

            ret += 'mkdir "%s/include_on_dvd/"\n' % (self.dvd_tmp_dir)
            ret += 'mv "%s" "%s/include_on_dvd/"\n' % (readme_file, self.dvd_tmp_dir)

        for toplevel_dir in self.files.keys():
            for photo_type in self.files[toplevel_dir].keys():
                dvd_dir = '%s/%s/%s' % \
                          (self.dvd_tmp_dir, toplevel_dir, self.phototypes[photo_type][0])
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

        ret += 'find "%s" -type f -exec chmod 644 {} \\;\n' % (self.dvd_tmp_dir)
        ret += 'cd "%s/.."\n' % (self.dvd_tmp_dir)
        ret += 'rm -f "%s"\n' % (self.dvd_zip_file)
        ret += 'zip -r "%s" "%s"\n' % (self.dvd_zip_file, os.path.basename(self.dvd_tmp_dir))
        ret += 'rm -rf "%s/"\n' % (self.dvd_tmp_dir)

        return ret


    def create_html_download_urls(self):
        return self.create_url(self.download_url, 'Supplemental DVD (ZIP)', self.dvd_zip_file)



def create_for_bulletin(bulletin):
    output_base_dir = cavedb.utils.get_output_base_dir(bulletin.id)
    dvd_tmp_dir = '%s/dvd' % (output_base_dir)

    return Dvd(get_bulletin_dvd_filename(bulletin.id), dvd_tmp_dir, \
               bulletin.dvd_readme, 'bulletin/%s/dvd' % (bulletin.id))


def get_bulletin_dvd_filename(bulletin_id):
    return '%s/dvd.zip' % (cavedb.utils.get_output_base_dir(bulletin_id))
