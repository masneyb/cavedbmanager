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

import cavedb.utils
import cavedb.docgen_latex_letter_bw
import cavedb.indexer_latex_underline

class LatexLetterDraft(cavedb.docgen_latex_letter_bw.LatexLetterBW):
    def __init__(self, bulletin):
        cavedb.docgen_latex_letter_bw.LatexLetterBW.__init__(self, bulletin, \
                       get_draft_tex_filename(bulletin.id), True, 'letterpaper')


    def create_html_download_urls(self):
        return self.create_url('bulletin/%s/draft_pdf' % \
                               (self.bulletin.id), \
                                'Draft PDF (No Images; Underlined Index Terms)', \
                                get_draft_pdf_filename(self.bulletin.id))


    def indexed_terms(self, terms):
        self.indexer = cavedb.indexer_latex_underline.IndexerLatexUnderline(terms)


def get_draft_tex_filename(bulletin_id):
    return '%s/pdf_draft/bulletin_%s.tex' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_draft_pdf_filename(bulletin_id):
    return '%s/pdf_draft/bulletin_%s.pdf' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
