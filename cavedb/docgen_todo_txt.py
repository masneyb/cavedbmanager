# SPDX-License-Identifier: Apache-2.0

import cavedb.docgen_common
import cavedb.utils

class TodoTxt(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self)
        self.bulletin = bulletin
        self.todofile = None


    def open(self, all_regions_gis_hash):
        # pylint: disable=consider-using-with
        filename = get_todo_txt_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.todofile = open(filename, 'w', encoding='utf-8')

        self.todofile.write('%s\n\n' % (self.bulletin.bulletin_name))


    def begin_region(self, region, gis_region_hash):
        self.todofile.write('%s\n' % (region.region_name))


    def feature_todo(self, feature, todo_enum, todo_descr):
        self.todofile.write('- %s - %s: %s\n' % (feature.name, todo_enum, todo_descr))


    def end_region(self):
        self.todofile.write('\n')


    def close(self):
        self.todofile.close()


    def create_html_download_urls(self):
        return self.create_url('bulletin/%s/todo' % \
                               (self.bulletin.id), 'TODO (TXT)', \
                                get_todo_txt_filename(self.bulletin.id))


def get_todo_txt_filename(bulletin_id):
    return '%s/todo/bulletin_%s_todo.txt' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
