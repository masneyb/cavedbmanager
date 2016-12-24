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

import cavedb.docgen_common
import cavedb.utils

class TodoTxt(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)


    def open(self, all_regions_gis_hash):
        filename = cavedb.utils.get_todo_txt_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.todofile = open(filename, 'w')

        self.todofile.write('%s\n\n' % (self.bulletin.bulletin_name))


    def begin_region(self, region, gis_region_hash, map_name):
        self.todofile.write('%s\n' % (region.region_name))


    def feature_todo(self, feature, todo_enum, todo_descr):
        self.todofile.write('- %s - %s: %s\n' % (feature.name, todo_enum, todo_descr))


    def end_region(self):
        self.todofile.write('\n')


    def close(self):
        self.todofile.close()

