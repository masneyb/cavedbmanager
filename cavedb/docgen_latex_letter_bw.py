# SPDX-License-Identifier: Apache-2.0

import cavedb.utils
import cavedb.docgen_latex_common

class LatexLetterBW(cavedb.docgen_latex_common.LatexCommon):
    def __init__(self, bulletin, filename=None, draft_mode=False, papersize='letterpaper'):
        if not filename:
            filename = get_bw_tex_filename(bulletin.id)

        cavedb.docgen_latex_common.LatexCommon.__init__(self, bulletin, filename, \
                                                        draft_mode, papersize)


    def get_gis_map_names(self):
        return cavedb.docgen_latex_common.get_bw_gis_map_names(self.bulletin)


    def get_photo_filename(self, photo):
        return cavedb.docgen_latex_common.get_bw_photo_filename(photo)


    def create_html_download_urls(self):
        return self.create_url('bulletin/%s/pdf' % \
                               (self.bulletin.id), 'PDF (B/W)', \
                                get_pdf_filename(self.bulletin.id))


def get_bw_tex_filename(bulletin_id):
    return '%s/pdf_bw/bulletin_%s.tex' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_pdf_filename(bulletin_id):
    return '%s/pdf_bw/bulletin_%s.pdf' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
