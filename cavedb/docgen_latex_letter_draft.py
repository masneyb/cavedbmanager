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

import cavedb.utils
import cavedb.docgen_latex_common
import cavedb.indexer_latex_boldface

class LatexLetterDraft(cavedb.docgen_latex_common.LatexCommon):
    def __init__(self, bulletin):
        cavedb.docgen_latex_common.LatexCommon.__init__(self, bulletin, \
                       get_draft_tex_filename(bulletin.id), True, 'letterpaper')


    def get_gis_map_names(self):
        return cavedb.docgen_latex_common.get_bw_gis_map_names(self.bulletin)


    def get_photo_filename(self, photo):
        return cavedb.docgen_latex_common.get_bw_photo_filename(photo)


    def create_html_download_urls(self):
        return self.create_url('/draft_pdf', 'Draft PDF (No Images; Bolded Index Terms)', \
                               get_draft_pdf_filename(self.bulletin.id))


    def indexed_terms(self, terms):
        self.indexer = cavedb.indexer_latex_boldface.IndexerLatexBoldface(terms)


def get_draft_tex_filename(bulletin_id):
    return '%s/pdf_draft/bulletin_%s.tex' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_draft_pdf_filename(bulletin_id):
    return '%s/pdf_draft/bulletin_%s.pdf' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
