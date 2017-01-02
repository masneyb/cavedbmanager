# Copyright 2016 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License")
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
import cavedb.models
import cavedb.utils
import cavedb.docgen_common
import cavedb.latex_indexer

class LatexCommon(cavedb.docgen_common.Common):
    def __init__(self, bulletin, filename, draft_mode, papersize):
        cavedb.docgen_common.Common.__init__(self, bulletin)
        self.filename = filename
        self.file_handle = None
        self.draft_mode = draft_mode
        self.papersize = papersize

        self.num_in_pdf = 1
        self.feature_attrs = None
        self.indexer = None
        self.gis_map_labels = {}
        self.list_of_photos = []
        self.list_of_caves = []
        self.photos_at_end = None
        self.entire_bulletin_refs = set([])


    def generate_buildscript(self):
        tex_dir = os.path.dirname(self.filename)
        bulletin_base_dir = cavedb.utils.get_bulletin_base_dir(self.bulletin.id)
        idx_file = self.filename.replace('.tex', '.idx')

        cd_cmd = 'cd %s\n' % (bulletin_base_dir)
        latex_cmd = 'pdflatex -output-directory %s %s\n' % (tex_dir, self.filename)
        makeidx_cmd = 'openout_any=a makeindex %s\n' % (idx_file)

        return cd_cmd + latex_cmd + makeidx_cmd + latex_cmd


    def indexed_terms(self, terms):
        self.indexer = cavedb.latex_indexer.LatexIndexer(terms)
        #self.indexer.dump_terms(self.file_handle)


    def open(self, all_regions_gis_hash):
        cavedb.docgen_common.create_base_directory(self.filename)
        self.file_handle = open(self.filename, 'w')

        self.__show_document_header()


    def begin_regions(self):
        self.__show_title_page()
        self.__show_preamble_page()
        self.__show_contributor_page()
        self.__show_toc()

        self.__writeln(r'\newpage')
        self.__writeln(r'\pagenumbering{arabic}')
        self.__writeln(r'')
        self.__writeln(r'% Change the header and footer for the document body')
        self.__writeln(r'\fancyfoot[LO,RE]{\thepage}')
        self.__writeln(r'\fancyfoot[LE,RO]{\textit{' + self.bulletin.bulletin_name + \
                     r' \\ \nouppercase\leftmark \nouppercase\rightmark}}')
        self.__writeln(r'')
        self.__writeln(r'\fancypagestyle{plain}{')
        self.__writeln(r'  \fancyfoot[LO,RE]{\thepage}')
        self.__writeln(r'  \fancyfoot[LE,RO]{\textit{' + self.bulletin.bulletin_name + '}}')
        self.__writeln(r'}')
        self.__writeln(r'')
        self.__writeln(r'')

        if self.bulletin.caves_header:
            self.__writeln(r'\chapter{Introduction}')
            self.__writeln(r'\begin{multicols}{2}')
            self.__writeln(r'\parindent 2ex')
            self.__writeln(self.__index_and_escape(self.bulletin.caves_header))
            self.__writeln(r'\parindent 0ex')
            self.__writeln(r'\end{multicols}')

        self.__writeln(r'\clearpage')

        self.__write_chapters(False)


    def close(self):
        self.__writeln(r'\appendix \def\chaptername{Appendix}')

        self.__write_chapters(True)

        self.__show_book_bibliography()
        self.__show_list_of_photos()
        self.__show_list_of_caves()

        self.__writeln(r'')
        self.__writeln(r'% Change the header and footer for the index')
        self.__writeln(r'\fancyfoot[LO,RE]{\thepage}')
        self.__writeln(r'\fancyfoot[LE,RO]{\textit{' + self.bulletin.bulletin_name + \
                     r' \\ \nouppercase\leftmark}}')
        self.__writeln(r'')
        self.__writeln(r'\fancypagestyle{plain}{')
        self.__writeln(r'  \fancyfoot[LO,RE]{\thepage}')
        self.__writeln(r'  \fancyfoot[LE,RO]{\textit ' + self.bulletin.bulletin_name + r'}}')
        self.__writeln(r'')
        self.__writeln(r'\printindex')
        self.__writeln(r'\end{document}')

        self.file_handle.close()


    def gis_map(self, gismap):
        if gismap.map_label:
            self.gis_map_labels[gismap] = gismap.map_label


    def __show_region_gis_maps(self, region):
        map_names = self.get_gis_map_names()
        if region.show_gis_map and len(map_names) > 0:
            for map_pos, map_name in enumerate(map_names):
                if map_pos > 0:
                    self.__writeln(r'\vspace*{8ex}')
                    self.__writeln(r'')

                image = cavedb.utils.get_region_gis_map(self.bulletin.id, region.id, map_name)

                self.__writeln(r'\begin{figure}[htp!]')
                self.__writeln(r'  \centering')
                self.__writeln(r'  \includegraphics[height=0.9\textheight,width=\textwidth,' + \
                             r'keepaspectratio=true]{' + image + '}')
                self.__writeln(r'\end{figure}')
                self.__writeln(r'')

                if map_pos == 0:
                    self.__writeln(r'\begin{figure}[htp!]')
                    self.__writeln(r'  \centering')
                    self.__writeln(r'  \includegraphics[width=\textwidth,keepaspectratio=true]{' + \
                                 r'../../gis_maps/legend.png}')
                    self.__writeln(r'\end{figure}')
                    self.__writeln(r'')

                if map_name in self.gis_map_labels:
                    self.__writeln(r'\begin{center} { \footnotesize \textit{' + \
                                 self.gis_map_labels[map_name] + r'}} \end{center}')
                    self.__writeln(r'')

                self.__writeln(r'')
                self.__writeln(r'\clearpage')
                self.__writeln(r'')


    def begin_region(self, region, gis_region_hash):
        self.photos_at_end = []

        self.__writeln(r'\clearpage')
        self.__writeln(r'\ifthenelse{\isodd{\value{page}}}{}{\hbox{}\newpage}')

        self.__writeln(r'\chapter{' + region.region_name + '}')

        self.__show_region_gis_maps(region)

        self.__writeln(r'\twocolumn')
        self.__writeln(r'\setlength\parskip{1ex plus 0in minus 0in}')

        if region.introduction:
            self.__writeln(r'\section*{Introduction} { ' + \
                         self.__index_and_escape(region.introduction) + ' }')
            self.__writeln(r'')


    def end_region(self):
        for feature, photo in self.photos_at_end:
            self.__show_feature_photo(feature, photo)

        self.__writeln(r'\onecolumn')


    def __show_document_header(self):
        draftstr = ',draft' if self.draft_mode else ''

        self.__writeln(r'\documentclass[10pt,' + self.papersize + ',leqno,twoside,openany' + \
                     draftstr + ']{book}')
        self.__writeln(r'\usepackage{etex}')
        self.__writeln(r'\reserveinserts{200}')
        self.__writeln(r'\usepackage[utf8]{inputenc}')
        self.__writeln(r'\usepackage{amsmath,amssymb,amsfonts}')
        self.__writeln(r'\usepackage{graphicx}')
        self.__writeln(r'\usepackage{multicol}')
        self.__writeln(r'\usepackage{fancyhdr}')
        self.__writeln(r'\usepackage{longtable}')
        self.__writeln(r'\usepackage{colortbl}')
        self.__writeln(r'\usepackage{helvet}')
        self.__writeln(r'\usepackage{tikz}')
        self.__writeln(r'\usepackage{hyphenat}')
        self.__writeln(r'\usepackage{ifthen}')
        self.__writeln(r'\usepackage{makeidx}')
        self.__writeln(r'\usepackage[maxfloats=145]{morefloats}')
        self.__writeln(r'')
        self.__writeln(r'\tikzstyle{mybox} = [draw=black, fill=gray!20, rectangle, ' + \
                     r'rounded corners, inner sep=5pt, inner ysep=7pt]')
        self.__writeln(r'')
        self.__writeln(r'% Note: always include this package last')
        self.__writeln(r'\usepackage[pdftitle={' + self.bulletin.bulletin_name + '},' + \
                     r'pdfauthor={' + self.bulletin.editors + '}, plainpages=false, ' + \
                     r'pdfpagelabels]{hyperref}')
        self.__writeln(r'')
        self.__writeln(r'\sloppy')
        self.__writeln(r'\raggedbottom')
        self.__writeln(r'\raggedcolumns')
        self.__writeln(r'\hbadness=10000')
        self.__writeln(r'\clubpenalty=10000')
        self.__writeln(r'\widowpenalty=10000')
        self.__writeln(r'')
        self.__writeln(r'\renewcommand{\thefigure}{}')
        self.__writeln(r'\renewcommand{\figurename}{}')
        self.__writeln(r'')
        self.__writeln(r'%\renewcommand{\familydefault}{\sfdefault}')
        self.__writeln(r'')
        self.__writeln(r'\makeatletter')
        self.__writeln(r'')
        self.__writeln(r'\renewcommand{\l@chapter}{\@dottedtocline{1}{1.5em}{2.3em}}')
        self.__writeln(r'')

        self.__writeln(r'\renewcommand{\@makechapterhead}[1]{')
        self.__writeln(r'\vspace*{10 pt}')
        self.__writeln(r'{\bfseries\LARGE \begin{centering} \nohyphens{#1} \\ \end{centering} }')
        self.__writeln(r'}')
        self.__writeln(r'\renewcommand{\section}{\@startsection {section}{1}{0pt}')
        self.__writeln(r'  {0ex}')
        self.__writeln(r'  {1px}')
        self.__writeln(r'  {\bf\Large}}')
        self.__writeln(r'')
        self.__writeln(r'\setlength{\abovecaptionskip}{0pt}')
        self.__writeln(r'\setlength{\belowcaptionskip}{2pt}')
        self.__writeln(r'')
        self.__writeln(r'\long\def\@makecaption#1#2{%')
        self.__writeln(r'   \vskip\abovecaptionskip')
        self.__writeln(r'   \hspace{0.05\linewidth}\begin{minipage}[t]{0.9\linewidth}\centering' + \
                     r'\footnotesize#2\par\end{minipage}\hspace{0.05\linewidth}')
        self.__writeln(r'   \vskip\belowcaptionskip}')
        self.__writeln(r'')
        self.__writeln(r'\makeatother')
        self.__writeln(r'')
        self.__writeln(r'\setlength\voffset{0in}')
        self.__writeln(r'\setlength\topmargin{-0.5in}')
        self.__writeln(r'\setlength\headheight{0in}')
        self.__writeln(r'\setlength\headsep{0in}')
        self.__writeln(r'\setlength\topskip{0in}')
        self.__writeln(r'')
        self.__writeln(r'\setlength\hoffset{0in}')
        self.__writeln(r'\setlength\oddsidemargin{-0.25in}')
        self.__writeln(r'\setlength\evensidemargin{-0.25in}')
        self.__writeln(r'\setlength\rightmargin{-0.25in}')
        self.__writeln(r'\setlength\textwidth{7in}')
        self.__writeln(r'\setlength\textheight{9.5in}')
        self.__writeln(r'')
        self.__writeln(r'\setlength\parindent{0.0in}')
        self.__writeln(r'\setlength\parskip{1ex plus 0in minus 0in}')
        self.__writeln(r'\setlength{\topsep}{0in plus 0in minus 0in}')
        self.__writeln(r'')
        self.__writeln(r'\pagestyle{fancy}')
        self.__writeln(r'')
        self.__writeln(r'\renewcommand{\sectionmark}[1]{\markright{ - #1}}')
        self.__writeln(r'\renewcommand{\headrulewidth}{0.0pt}')
        self.__writeln(r'\renewcommand{\footrulewidth}{0.4pt}')
        self.__writeln(r'\fancyhead[LE,RO]{}')
        self.__writeln(r'\fancyhead[LO,RE]{}')
        self.__writeln(r'\fancyfoot[C]{}')
        self.__writeln(r'')
        self.__writeln(r'')
        self.__writeln(r'% This is the header and footer for the preamble pages. It is changed')
        self.__writeln(r'% later on when the document body is shown.')
        self.__writeln(r'')
        self.__writeln(r'\fancyfoot[LE,RO]{\thepage}')
        self.__writeln(r'\fancyfoot[LO,RE]{\textit{' + self.bulletin.bulletin_name + '}}')
        self.__writeln(r'')
        self.__writeln(r'\fancypagestyle{plain}{')
        self.__writeln(r'  \fancyfoot[LE,RO]{\thepage}')
        self.__writeln(r'  \fancyfoot[LO,RE]{\textit{' + self.bulletin.bulletin_name + '}}')
        self.__writeln(r'}')
        self.__writeln(r'')
        self.__writeln(r'')
        self.__writeln(r'\setcounter{topnumber}{4}')
        self.__writeln(r'\setcounter{dbltopnumber}{2}')
        self.__writeln(r'\setcounter{bottomnumber}{0}')
        self.__writeln(r'\setcounter{totalnumber}{4}')
        self.__writeln(r'')
        self.__writeln(r'\renewcommand{\topfraction}{0.6}')
        self.__writeln(r'\renewcommand{\bottomfraction}{0}')
        self.__writeln(r'\renewcommand{\textfraction}{0.3}')
        self.__writeln(r'\renewcommand{\floatpagefraction}{0.5}')
        self.__writeln(r'\renewcommand{\dbltopfraction}{0.7}')
        self.__writeln(r'\renewcommand{\dblfloatpagefraction}{0.7}')
        self.__writeln(r'')
        self.__writeln(r'\pagenumbering{roman}')
        self.__writeln(r'\makeindex')
        self.__writeln(r'')
        self.__writeln(r'\begin{document}')

    def __show_title_page(self):
        self.__writeln(r'')
        self.__writeln(r'% ---- Title Page ----')
        self.__writeln(r'')
        self.__writeln(r'\clearpage')
        self.__writeln(r'\thispagestyle{empty}')
        self.__writeln(self.__index_and_escape(self.bulletin.title_page))
        self.__writeln(r'\newpage')
        self.__writeln(r'')


    def __show_preamble_page(self):
        self.__writeln(r'')
        self.__writeln(r'\clearpage')
        self.__writeln(r'\thispagestyle{empty}')
        self.__writeln(self.__index_and_escape(self.bulletin.preamble_page))
        self.__writeln(r'\newpage')
        self.__writeln(r'')


    def __show_contributor_page(self):
        self.__writeln(r'')
        self.__writeln(r'\clearpage')
        self.__writeln(self.__index_and_escape(self.bulletin.contributor_page))
        self.__writeln(r'\newpage')
        self.__writeln(r'')


    def __show_toc(self):
        self.__writeln(r'')
        self.__writeln(r'\clearpage')
        self.__writeln(r'\tableofcontents')
        self.__writeln(r'\clearpage')
        self.__writeln(r'')

        if self.bulletin.toc_footer:
            self.__writeln(self.__index_and_escape(self.bulletin.toc_footer))

        self.__writeln(r'')


    # Note: You must override this method in a subclass
    def get_gis_map_names(self):
        return None

    def __write(self, line):
        self.file_handle.write(line.replace('\r', ''))


    def __writeln(self, line):
        self.__write(line + '\n')


    def begin_feature(self, feature):
        self.num_in_pdf = 1

        self.feature_attrs = {}
        self.feature_attrs['feature'] = feature
        self.feature_attrs['entrances'] = []
        self.feature_attrs['photos'] = []
        self.feature_attrs['refmaps'] = []
        self.feature_attrs['refs'] = []


    def feature_entrance(self, feature, entrance, coordinates):
        self.feature_attrs['entrances'].append((entrance, coordinates))


    def feature_photo(self, feature, photo):
        if not photo.show_in_pdf:
            return

        if photo.show_at_end:
            self.photos_at_end.append((feature, photo))
        else:
            self.feature_attrs['photos'].append(photo)


    def feature_referenced_map(self, feature, refmap):
        self.feature_attrs['refmaps'].append(refmap)


    def feature_reference(self, feature, ref):
        self.feature_attrs['refs'].append(ref)


    def __feature_names(self, feature):
        self.__writeln(r'\begin{centering}')

        self.__writeln(r'{\Large \bfseries \uppercase{' + escape(feature.name) + r'} } \\*')

        alt_names = cavedb.utils.comma_split(feature.alternate_names)
        if len(alt_names) > 0:
            self.__writeln(r'{\large \bfseries (' + escape(', '.join(alt_names)) + r')} \\[2ex]')

        self.__writeln(r'\end{centering}')


    def __feature_length_and_depth(self, feature):
        if not feature.length_ft or feature.length_ft <= 0:
            return

        approx = r'$\sim$' if feature.length_based_on == 'estimate' else ''

        if feature.length_ft < 5280:
            length_str = '{:,} ft'.format(feature.length_ft)
        else:
            length_str = '{:,} mi'.format(round(feature.length_ft / 5280.0, 1))

        self.__write(r'Length: %s%s' % (approx, length_str))

        if feature.depth_ft:
            depth_str = '{:,} ft'.format(feature.depth_ft)

            self.__write(r' \hfill Depth: %s%s' % (approx, depth_str))

        self.__writeln(r' \\*')


    def __show_coordinates(self, entrance, coordinates):
        hemisphere = 'N ' if coordinates.utmzone.utm_north else 'S '
        self.__writeln(r'NAD27 UTM: \hfill ' + str(coordinates.utmzone.utm_zone) + hemisphere + \
                     '%.0f' % (coordinates.nad27_utmnorth) + r'N ' + \
                     '%.0f' % (coordinates.nad27_utmeast) + r'E \\*')

        self.__writeln(r'WGS84 Lat/Lon: \hfill ' + \
                     decimal_degrees_to_ddmmss_str(coordinates.wgs84_lat) + r' / ' + \
                     decimal_degrees_to_ddmmss_str(coordinates.wgs84_lon) + r' \\*')

        if entrance.elevation_ft:
            self.__write('Elevation: {:,}'.format(entrance.elevation_ft) + '\'')
        if entrance.quad:
            self.__write(r' \hfill ' + entrance.quad.quad_name + r' Quad')
        if entrance.elevation_ft or entrance.quad:
            self.__writeln(r' \\*')

        if entrance.coord_acquision == 'GPS':
            self.__writeln(r'\textit{Coordinates acquired using a GPS receiver.} \\*')
        elif entrance.coord_acquision == 'Other Topo Map':
            self.__writeln(r'\textit{Coordinates acquired off of a topo map.} \\*')
        elif entrance.coord_acquision == '7.5 Topo Map':
            self.__writeln(r'\textit{Coordinates acquired off of a 7.5\' topo map.} \\*')
        elif entrance.coord_acquision == 'Google Earth':
            self.__writeln(r'\textit{Coordinates acquired using Google Earth.} \\*')
        elif entrance.coord_acquision == 'Estimate':
            self.__writeln(r'\textit{Coordinates are an estimate.} \\*')
        elif entrance.coord_acquision == 'Filled In':
            self.__writeln(r'\textit{Entrance is filled in; coordinates are an estimate.} \\*')
        else:
            self.__writeln(r'\textit{Unknown coordinate acquisition method.} \\*')


    def __show_feature_header(self, feature):
        self.__writeln(r'\vspace{1ex}')
        self.__writeln(r'')
        self.__writeln(r'\begin{tikzpicture}')
        self.__writeln(r'\node [mybox] (box){')
        self.__writeln(r'\begin{minipage}[b]{0.95\columnwidth}')
        self.__writeln(r'\phantomsection')
        self.__writeln(r'\label{feature' + str(feature.id) + r'}')

        self.__feature_names(feature)

        self.__feature_length_and_depth(feature)

        has_coordinates = False
        for counter, (entrance, coordinates) in enumerate(self.feature_attrs['entrances']):
            if counter > 0:
                self.__writeln(r' \\')

            if entrance.entrance_name and entrance.entrance_name != feature.name:
                self.__writeln(r'\textit{\textbf{' + escape(entrance.entrance_name) + r'}} \\*')

            if coordinates.wgs84_lat:
                has_coordinates = True
                self.__show_coordinates(entrance, coordinates)

        if not has_coordinates:
            self.__writeln(r'\textit{Coordinates are not available.} \\*')

        self.__writeln(r'\vspace{-2ex}')
        self.__writeln(r'\end{minipage}')
        self.__writeln(r'};')
        self.__writeln(r'\index{' + escape(feature.name) + '|(}')
        self.__writeln(r'\end{tikzpicture}')
        self.__writeln(r'\nopagebreak[4]')


    def __show_feature_body(self, feature):
        self.__write_paragraphs('\n{ \\bf ', feature.hazards, ' }\n\n')

        if not self.__write_paragraphs(None, feature.description, None):
            self.__writeln('There is currently no description available.\n')

        self.__write_paragraphs('\n\n', feature.geology_hydrology, None)

        self.__write_paragraphs('\n\n{ \\bf Biology:} ', feature.biology, None)

        self.__write_paragraphs('\n\n{ \\bf History:} ', feature.history, None)

        if feature.source:
            self.__write(r' \textit{(' + feature.source.strip() + r')}')

        self.__writeln(r'')
        self.__writeln(r'')

        self.__show_references(self.feature_attrs['refs'])

        self.__writeln(r'\index{' + escape(feature.name) + r'|)}')


    def __add_to_caves_index(self, feature):
        if feature.survey_id:
            survey_id = '%s%s' % (feature.survey_county.survey_short_name, feature.survey_id)
        else:
            survey_id = ''

        feature_page_ref = r'\pageref{feature' + str(feature.id) + r'}'
        map_page_ref = ''
        ent_page_ref = ''

        for photo in self.feature_attrs['photos']:
            if photo.type == 'map' and map_page_ref == '':
                map_page_ref = r'\pageref{photo' + str(photo.id) + r'}'
            if photo.type == 'entrance_picture' and not ent_page_ref:
                ent_page_ref = r'\pageref{photo' + str(photo.id) + r'}'

        if map_page_ref == '' and len(self.feature_attrs['refmaps']) > 0:
            map_page_ref = r'\pageref{photo' + str(self.feature_attrs['refmaps'][0].map.id) + r'}'

        for alias in cavedb.utils.get_all_feature_alt_names(feature):
            see_label = escape(alias) + r'\begin{description}' + '\n' + \
                        r'\setlength{\parskip}{-2ex plus 0in minus 0in}' + '\n' + \
                        r'\item \textit{see ' + escape(feature.name) + \
                        r'\vspace{-2ex} } \end{description}'

            self.list_of_caves.append(see_label + ' & ' + escape(survey_id) + r' & ' + \
                                      escape(feature.feature_type) + r' &  - &  - & ' + \
                                      feature_page_ref + ' & ' + map_page_ref + r' & ' + \
                                      ent_page_ref + r' \\')

        length_str = r'{:,}$^\prime$'.format(feature.length_ft) if feature.length_ft else ''
        depth_str = r'{:,}$^\prime$'.format(feature.depth_ft) if feature.depth_ft else ''

        self.list_of_caves.append(escape(feature.name) + ' & ' + escape(survey_id) + r' & ' + \
                                  escape(feature.feature_type) + r' & ' + length_str + ' & ' + \
                                  depth_str + ' & ' + feature_page_ref + ' & ' + map_page_ref + \
                                  r' & ' + ent_page_ref + r' \\')


    def end_feature(self):
        feature = self.feature_attrs['feature']

        for photo in self.feature_attrs['photos']:
            self.__show_feature_photo(feature, photo)

        self.__show_feature_header(feature)

        self.__show_feature_body(feature)

        self.__add_to_caves_index(feature)


    # Note: You must override this method in a subclass
    def get_photo_filename(self, photo):
        return None


    def __show_feature_photo(self, feature, photo):
        if self.num_in_pdf % 48 == 0:
            self.__writeln(r'\clearpage')

        figure_opts = '*' if photo.scale != 'column' else ''

        graphic_opts = 'keepaspectratio'
        graphic_opts += ',angle=%s' % (photo.rotate_degrees if photo.rotate_degrees else 0)

        if photo.scale == 'fullpage':
            if photo.caption:
                graphic_opts += r',height=0.9\textheight,width=\textwidth'
            else:
                graphic_opts += r',height=\textheight,width=\textwidth'
        elif photo.scale == 'halfpage':
            graphic_opts += r',height=0.4\textheight,width=\textwidth'
        else:
            graphic_opts += r',height=.4\textheight,width=\columnwidth'

        self.__writeln(r'\begin{figure' + figure_opts + '}[tp]')
        self.__writeln(r'\phantomsection')

        self.__write(r'\index{' + escape(feature.name) + '}')
        if photo.indexed_terms:
            for term in cavedb.utils.newline_split(photo.indexed_terms):
                self.__write(r'\index{' + escape(term) + '}')
        self.__writeln(r'')

        self.__writeln(r'\centering')

        url = self.get_photo_filename(photo)
        self.__writeln(r'\includegraphics[' + graphic_opts + r']{' + url + r'}')

        if photo.caption:
            self.__writeln(r'\caption{' + self.__format_photo_caption(feature, photo.caption) + \
                           r'}')

        self.__writeln(r'\label{photo' + str(photo.id) + r'}')
        self.__writeln(r'\end{figure' + figure_opts + '}')

        self.__writeln(r'')
        self.__writeln(r'')

        if photo.type != 'map':
            self.list_of_photos.append(r'\pageref{photo' + str(photo.id) + r'}  & ' + \
                                       escape(feature.name) + r' & ' +
                                       escape(photo.people_shown) + r' & ' + \
                                       escape(photo.author) + r' \\')


    def __format_photo_caption(self, feature, caption):
        caption = add_caption_hbox(caption, feature.name.strip())

        for alias in cavedb.utils.get_all_feature_alt_names(feature):
            caption = add_caption_hbox(caption, alias)

        for (entrance, coordinates) in self.feature_attrs['entrances']:
            if entrance.entrance_name and entrance.entrance_name != feature.name:
                caption = add_caption_hbox(caption, entrance.entrance_name.strip())

        return escape(convert_quotes(caption))


    def __show_references(self, refs):
        num_refs = len(refs)
        if num_refs == 0:
            return

        refs_by_date = {}
        for ref in refs:
            parsed_date = cavedb.utils.get_normalized_date(ref.date) + none_to_empty(ref.volume) + \
                          none_to_empty(ref.number) + none_to_empty(ref.pages) + \
                          none_to_empty(ref.book) + none_to_empty(ref.title)

            if parsed_date not in refs_by_date:
                refs_by_date[parsed_date] = []

            refstr = reference_to_string(ref)
            refs_by_date[parsed_date].append(refstr)

            # For the global bibliography
            self.entire_bulletin_refs.add(refstr)

        self.__writeln(r'{ \footnotesize')
        self.__writeln(r'\leftskip 0.2in')
        self.__writeln(r'\parindent -0.1in')

        counter = 0
        for parsed_date in sorted(refs_by_date):
            for refstr in refs_by_date[parsed_date]:
                counter = counter + 1

                if counter < 3 or counter % 2 == 0 or counter == num_refs:
                    self.__writeln(r'\nopagebreak[4]')

                if counter > 1:
                    self.__writeln(r'\vspace{-3.5ex}')

                self.__writeln(refstr)

        self.__writeln('}')

        self.__writeln(r'')
        self.__writeln(r'')


    def __show_book_bibliography(self):
        self.__writeln(r'\chapter{Bibliography}')
        self.__writeln(r'\begin{multicols}{2}')
        self.__writeln(r'{')
        self.__writeln(r'\setlength{\parskip}{-2ex plus 0in minus 0in}')
        self.__writeln(r'\parindent -0.1in')
        self.__writeln(r'\leftskip 0.2in')
        self.__writeln(r'\it')
        self.__writeln(r'\footnotesize')

        for refstr in sorted(self.entire_bulletin_refs):
            self.__writeln(refstr)

        self.__writeln(r'')
        self.__writeln(r'}')
        self.__writeln(r'\end{multicols}')


    def __show_list_of_photos(self):
        self.__writeln(r'\chapter{List of Photos}')
        self.__writeln(r'\begin{center}')
        self.__writeln(r'\begin{longtable}{|c| p{5cm} | p{5cm} | p{5cm} |}')
        self.__writeln(r'    %This is the header for the first page of the table...')
        self.__writeln(r'    \hline')
        self.__writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Page & Cave & ' + \
                       r'People Shown In Photo & Photographer \\')
        self.__writeln(r'    \hline')
        self.__writeln(r'  \endfirsthead')
        self.__writeln(r'')
        self.__writeln(r'    %This is the header for the remaining page(s) of the table...')
        self.__writeln(r'    \hline')
        self.__writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Page & Cave & ' + \
                       r'People Shown In Photo & Photographer \\')
        self.__writeln(r'    \hline')
        self.__writeln(r'  \endhead')
        self.__writeln(r'')
        self.__writeln(r'    %This is the footer for all pages except the last page of the table.')
        self.__writeln(r'    \hline')
        self.__writeln(r'  \endfoot')
        self.__writeln(r'')
        self.__writeln(r'    %This is the footer for the last page of the table...')
        self.__writeln(r'    \hline ')
        self.__writeln(r'  \endlastfoot')

        if self.bulletin.photo_index_header:
            self.__writeln(escape(self.bulletin.photo_index_header))

        for counter, photo in enumerate(self.list_of_photos):
            if counter % 2 != 0:
                self.__write(r'\rowcolor[rgb]{0.95,0.95,0.95} ')

            self.__writeln(photo)

        self.__writeln(r'\end{longtable}')
        self.__writeln(r'\end{center}')


    def __show_list_of_caves(self):
        self.__writeln(r'\chapter{Index of Caves}')
        self.__writeln(r'\begin{center}')
        self.__writeln(r'\begin{longtable}{| p{5.5cm} |c|c|c|c|c|c|c|}')
        self.__writeln(r'    %This is the header for the first page of the table...')
        self.__writeln(r'    \hline')
        self.__writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Name & ID & Type & ' + \
                       r'Length & Depth & Page & Map & Ent. \\')
        self.__writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} & & & & & & & Photo \\')
        self.__writeln(r'    \hline')
        self.__writeln(r'  \endfirsthead')
        self.__writeln(r'')
        self.__writeln(r'    %This is the header for the remaining page(s) of the table...')
        self.__writeln(r'    \hline')
        self.__writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Name & ID & Type & ' + \
                       r'Length & Depth & Page & Map & Ent. \\')
        self.__writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} & & & & & & & Photo \\')
        self.__writeln(r'    \hline')
        self.__writeln(r'  \endhead')
        self.__writeln(r'')
        self.__writeln(r'    %This is the footer for all pages except the last page of the table.')
        self.__writeln(r'    \hline')
        self.__writeln(r'  \endfoot')
        self.__writeln(r'')
        self.__writeln(r'    %This is the footer for the last page of the table...')
        self.__writeln(r'    \hline')
        self.__writeln(r'  \endlastfoot')

        self.list_of_caves.sort()
        for counter, cave in enumerate(self.list_of_caves):
            if counter % 2 != 0:
                self.__write(r'\rowcolor[rgb]{0.95,0.95,0.95} ')

            self.__writeln(cave)

        self.__writeln(r'\end{longtable}')
        self.__writeln(r'\end{center}')


    def __write_chapters(self, is_appendix):
        for chapter in cavedb.models.BulletinChapter.objects.filter(bulletin__id=self.bulletin.id):
            if chapter.is_appendix != is_appendix:
                continue

            self.__writeln(r'\chapter{' + escape(chapter.chapter_title) + r'}')

            for section in cavedb.models.BulletinSection.objects \
               .filter(bulletin_chapter__id=chapter.id):

                if section.section_title:
                    self.__writeln(r'\section{' + escape(section.section_title) + r'}')

                if section.section_subtitle:
                    self.__writeln(r'{\begin{centering} \small \textit{' + \
                                 escape(section.section_subtitle) + r'} \\* \end{centering} }')

                if section.num_columns > 1:
                    self.__writeln(r'\begin{multicols}{2}')

                self.__writeln(r'\parindent 2ex')

                self.__writeln(self.__index_and_escape(section.section_data))
                self.__writeln(r'')

                self.__writeln(r'\parindent 0ex')

                refs = []
                for ref in cavedb.models.BulletinSectionReference.objects \
                   .filter(bulletinsection__id=section.id):
                    refs.append(ref)

                self.__show_references(refs)

                if section.num_columns > 1:
                    self.__writeln(r'\end{multicols}')


    def __write_paragraphs(self, prefix, inputstr, suffix):
        if not inputstr:
            return False

        inputstr = convert_quotes(inputstr)

        first_para = True
        for para in cavedb.utils.newline_split(inputstr):
            if not para:
                continue

            if first_para:
                if prefix:
                    self.__write(prefix)
                first_para = False
            else:
                self.__writeln(r'')
                self.__writeln(r'')

            self.__write(escape(self.indexer.generate_index(para)))

        if not first_para:
            if suffix:
                self.__write(suffix)

        # Return whether or not paragraphs were shown.
        return not first_para


    def __index_and_escape(self, inputstr):
        if not inputstr:
            return ""

        return escape(convert_quotes(self.indexer.generate_index(inputstr.strip())))


# Add a \hbox{} around the cave and entrance names so that they appear on the
# same line in the PDF.
def add_caption_hbox(caption, name):
    if caption.startswith(name):
        return caption

    return caption.replace(name, r'\hbox{%s}' % (name))


def convert_quotes(inputstr):
    if not inputstr:
        return ""

    # Use em dashes
    inputstr = inputstr.replace(" - ", " -- ")

    # Use the directional quotes
    while True:
        if inputstr.count("\"") < 2:
            break

        inputstr = inputstr.replace("\"", "``", 1)
        inputstr = inputstr.replace("\"", "''", 1)

    return inputstr


def escape(inputstr):
    if not inputstr:
        return ""

    inputstr = inputstr.strip()

    # Escape the # for LaTeX
    return inputstr.replace('#', '\\#')


def none_to_empty(inputstr):
    return inputstr if inputstr else ''


def decimal_degrees_to_ddmmss_str(decdegs):
    positive = decdegs >= 0
    mins, secs = divmod(abs(decdegs) * 3600, 60)
    degs, mins = divmod(mins, 60)
    degs = degs if positive else -degs

    return '%.0f$^\\circ$ %02d\' %s"' % (degs, mins, ('%.1f' % (secs)).zfill(4))


def reference_to_string(ref):
    parts = []
    if ref.author:
        parts.append(escape(convert_quotes(ref.author)))

    if ref.title:
        parts.append(escape(convert_quotes(ref.title)))

    if ref.book:
        parts.append(r'\textnormal{``' + escape(convert_quotes(ref.book)) + '\'\'}')

    if ref.volume:
        vnp = r'V' + escape(convert_quotes(ref.volume))

        if ref.number:
            vnp = vnp + r'n' + escape(convert_quotes(ref.number))

        if ref.pages:
            vnp = vnp + r'p'
            if '-' in ref.pages or ',' in ref.pages:
                vnp = vnp + r'p'
            vnp += escape(convert_quotes(ref.pages))

        if vnp:
            parts.append(vnp)

    if ref.url:
        parts.append(r'URL: ' + escape(convert_quotes(ref.url)))

    if ref.extra:
        parts.append(escape(convert_quotes(ref.extra)))

    if ref.date:
        parts.append(escape(convert_quotes(ref.date)))
    else:
        parts.append('date unknown')

    if not ref.volume and ref.pages:
        if '-' in ref.pages or ',' in ref.pages:
            parts.append('Pages ' + escape(convert_quotes(ref.pages)))
        else:
            parts.append('Page ' + escape(convert_quotes(ref.pages)))

    return r'\textit{' + ', '.join(parts) + r'} \\' + '\n'


def get_bw_photo_filename(photo):
    if photo.secondary_filename:
        return photo.secondary_filename.path

    return photo.filename.path


def get_color_photo_filename(photo):
    if photo.filename:
        return photo.filename.path

    return photo.secondary_filename.path


def get_bw_gis_map_names(bulletin):
    ret = []

    if bulletin.bw_map1:
        ret.append(bulletin.bw_map1)
    if bulletin.bw_map2:
        ret.append(bulletin.bw_map2)
    if bulletin.bw_map3:
        ret.append(bulletin.bw_map3)

    return ret


def get_color_gis_map_names(bulletin):
    ret = []

    if bulletin.color_map1:
        ret.append(bulletin.color_map1)
    if bulletin.color_map2:
        ret.append(bulletin.color_map2)
    if bulletin.color_map3:
        ret.append(bulletin.color_map3)

    return ret

