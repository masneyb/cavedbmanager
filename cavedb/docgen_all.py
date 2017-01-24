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

from cavedb.docgen_composite import Composite
import cavedb.docgen_dvd
import cavedb.docgen_entrance_csv
import cavedb.docgen_gis_maps
import cavedb.docgen_gpx
import cavedb.docgen_kml
import cavedb.docgen_latex_letter_bw
import cavedb.docgen_latex_letter_color
import cavedb.docgen_latex_letter_draft
import cavedb.docgen_mapserver_mapfile
import cavedb.docgen_mxf
import cavedb.docgen_shp
import cavedb.docgen_text
import cavedb.docgen_todo_txt

# Documents that span a single bulletin
def create_bulletin_docgen_classes(bulletin):
    return Composite([cavedb.docgen_dvd.create_for_bulletin(bulletin),
                      cavedb.docgen_entrance_csv.create_for_bulletin(bulletin),
                      cavedb.docgen_gpx.create_for_bulletin(bulletin),
                      cavedb.docgen_kml.create_for_bulletin(bulletin),
                      cavedb.docgen_mxf.create_for_bulletin(bulletin),
                      cavedb.docgen_text.Text(bulletin),
                      cavedb.docgen_todo_txt.TodoTxt(bulletin),

                      # The SHP and mapserver files need to be created before the GisMaps.
                      cavedb.docgen_shp.create_for_bulletin(bulletin),
                      cavedb.docgen_mapserver_mapfile.MapserverMapfile(bulletin),
                      cavedb.docgen_gis_maps.GisMaps(bulletin),

                      # Create the LaTeX PDFs last since they depend on other resources.
                      cavedb.docgen_latex_letter_draft.LatexLetterDraft(bulletin),
                      cavedb.docgen_latex_letter_bw.LatexLetterBW(bulletin),
                      cavedb.docgen_latex_letter_color.LatexLetterColor(bulletin),
                     ])


# Documents that span all bulletins
def create_global_docgen_classes():
    return Composite([cavedb.docgen_entrance_csv.create_for_global(),
                      cavedb.docgen_gpx.create_for_global(),
                      cavedb.docgen_kml.create_for_global(),
                      cavedb.docgen_mxf.create_for_global(),
                      cavedb.docgen_shp.create_for_global(),
                     ])


def get_bulletin_download_links(bulletin):
    docgen = create_bulletin_docgen_classes(bulletin)
    return docgen.create_html_download_urls()
