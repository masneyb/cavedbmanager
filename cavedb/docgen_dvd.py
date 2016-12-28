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
import cavedb.models
import cavedb.settings

class Dvd(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)
        self.files = {}

        # Tuple contains (Directory Name, File Suffix)
        self.phototypes = {}
        self.phototypes['map'] = ('Maps', 'Map')
        self.phototypes['entrance_picture'] = ('Entrance Photos', 'Entrance Photo')
        self.phototypes['in_cave_picture'] = ('In Cave Photos', 'In Cave Photo')
        self.phototypes['surface_picture'] = ('Surface Photos', 'Surface Photo')
        self.phototypes['drawing'] = ('Drawings', 'Drawing')
        self.phototypes['other'] = ('Others', 'Other')


    def feature_photo(self, feature, photo):
        if not photo.include_on_dvd:
            return

        if photo.type not in self.files:
            self.files[photo.type] = {}

        if feature.name not in self.files[photo.type]:
            self.files[photo.type][feature.name] = []

        meta = {}
        meta['src'] = '%s/%s' % (cavedb.settings.MEDIA_ROOT, photo.filename)
        if photo.author:
            meta['author'] = photo.author

        self.files[photo.type][feature.name].append(meta)


    def generate_buildscript(self):
        output_base_dir = cavedb.utils.get_output_base_dir(self.bulletin.id)
        dvd_tmp_dir = '%s/dvd' % (output_base_dir)

        readme_file = '%s/README.txt' % (cavedb.utils.get_output_base_dir(self.bulletin.id))
        with open(readme_file, 'w') as output:
            output.write(self.bulletin.dvd_readme)

        ret = 'rm -rf "%s/"\n' % (dvd_tmp_dir)
        ret += 'mkdir -p "%s"\n' % (dvd_tmp_dir)
        ret += 'mv "%s" "%s/"\n' % (readme_file, dvd_tmp_dir)

        for photo_type in self.files.keys():
            dvd_dir = '%s/%s' % (dvd_tmp_dir, self.phototypes[photo_type][0])
            ret += 'mkdir -p "%s"\n' % (dvd_dir)

            for feature_name in self.files[photo_type].keys():
                num_photos = len(self.files[photo_type][feature_name])
                photo_num = 1

                for photo_meta in self.files[photo_type][feature_name]:
                    destfile = '%s/%s %s' % (dvd_dir, feature_name, self.phototypes[photo_type][1])

                    if num_photos > 1:
                        destfile += ' - %02d of %02d' % (photo_num, num_photos)
                        photo_num = photo_num + 1

                    if 'author' in photo_meta:
                        destfile += ' - %s' % (photo_meta['author'])

                    extpos = photo_meta['src'].rfind('.')
                    destfile += photo_meta['src'][extpos:]

                    ret += 'ln "%s" "%s"\n' % (photo_meta['src'], destfile)

        dvd_zip_file = cavedb.utils.get_dvd_filename(self.bulletin.id)
        ret += 'cd %s\n' % (output_base_dir)
        ret += 'zip -r "%s" "%s"\n' % (dvd_zip_file, os.path.basename(dvd_tmp_dir))
        ret += 'rm -rf "%s/"\n' % (dvd_tmp_dir)

        return ret

