# SPDX-License-Identifier: Apache-2.0

import cavedb.utils
import cavedb.docgen_latex_common

class LatexLetterColor(cavedb.docgen_latex_common.LatexCommon):
    def __init__(self, bulletin):
        cavedb.docgen_latex_common.LatexCommon.__init__(self, bulletin, \
                       get_color_tex_filename(bulletin.id), False, 'letterpaper')


    def get_gis_map_names(self):
        return cavedb.docgen_latex_common.get_color_gis_map_names(self.bulletin)


    def get_photo_filename(self, photo):
        return cavedb.docgen_latex_common.get_color_photo_filename(photo)


    def create_html_download_urls(self):
        return self.create_url('bulletin/%s/color_pdf' % \
                               (self.bulletin.id), 'PDF (Color)', \
                                get_color_pdf_filename(self.bulletin.id))


def get_color_tex_filename(bulletin_id):
    return '%s/pdf_color/bulletin_%s.tex' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_color_pdf_filename(bulletin_id):
    return '%s/pdf_color/bulletin_%s.pdf' % \
           (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
