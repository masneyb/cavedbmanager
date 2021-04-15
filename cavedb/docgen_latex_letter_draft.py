# SPDX-License-Identifier: Apache-2.0

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
