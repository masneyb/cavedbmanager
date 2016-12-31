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

import re
import datetime
import dateutil.parser
import dateutil.relativedelta
import cavedb.models
import cavedb.utils
import cavedb.docgen_common

# TODO AFTER - look for trailing space at end of strings

class LatexCommon(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin, filename, draft_mode, papersize):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)
        self.filename = filename
        self.file_handle = None
        self.draft_mode = draft_mode
        self.papersize = papersize

        self.num_in_pdf = 1
        self.feature_attrs = None
        self.indexed_terms = None
        self.gis_map_labels = {}
        self.list_of_photos = []
        self.list_of_caves = []


    def open(self, all_regions_gis_hash):
        cavedb.docgen_common.create_base_directory(self.filename)
        self.file_handle = open(self.filename, 'w')

        self.indexed_terms = self.get_indexed_terms()

        self.__show_document_header()
        self.__show_title_page()
        self.__show_preamble_page()
        self.__show_contributor_page()
        self.__show_toc()

        self.writeln(r'\newpage')
        self.writeln(r'\pagenumbering{arabic}')
        self.writeln(r'')
        self.writeln(r'% Change the header and footer for the document body')
        self.writeln(r'\fancyfoot[LO,RE]{\thepage}')
        self.writeln(r'\fancyfoot[LE,RO]{\textit{' + self.bulletin.bulletin_name + \
                     r' \\ \nouppercase\leftmark \nouppercase\rightmark}}')
        self.writeln(r'')
        self.writeln(r'\fancypagestyle{plain}{')
        self.writeln(r'  \fancyfoot[LO,RE]{\thepage}')
        self.writeln(r'  \fancyfoot[LE,RO]{\textit{' + self.bulletin.bulletin_name + '}}')
        self.writeln(r'} ')
        self.writeln(r'')
        self.writeln(r'')

        if self.bulletin.caves_header:
            self.writeln(r'\chapter{Introduction}')
            self.writeln(r'\begin{multicols}{2}')
            self.writeln(r'\parindent 2ex')
            self.writeln(escape(self.generate_index(self.bulletin.caves_header.strip())))
            self.writeln(r'\parindent 0ex')
            self.writeln(r'\end{multicols}')

        self.writeln(r'\clearpage')

        self.write_chapters(False)


    def close(self):
        self.writeln(r'\appendix \def\chaptername{Appendix}')

        self.write_chapters(True)

        self.__show_book_bibliography()
        self.__show_list_of_photos()
        self.__show_list_of_caves()

        self.writeln(r'')
        self.writeln(r'') # TODO AFTER - remove
        self.writeln(r'% Change the header and footer for the index')
        self.writeln(r'\fancyfoot[LO,RE]{\thepage}')
        self.writeln(r'\fancyfoot[LE,RO]{\textit{' + self.bulletin.bulletin_name + \
                     r' \\ \nouppercase\leftmark}}')
        self.writeln(r'')
        self.writeln(r'\fancypagestyle{plain}{')
        self.writeln(r'  \fancyfoot[LO,RE]{\thepage}')
        self.writeln(r'  \fancyfoot[LE,RO]{\textit' + self.bulletin.bulletin_name + r'}}')
        self.writeln(r'')
        self.writeln(r'\printindex')
        self.writeln(r'\end{document}')

        self.file_handle.close()


    def gis_map(self, gismap):
        if gismap.map_label:
            self.gis_map_labels[gismap] = gismap.map_label


    def __show_region_gis_maps(self, region):
        map_names = self.get_gis_map_names()
        if region.show_gis_map and len(map_names) > 0:
            for map_pos, map_name in enumerate(map_names):
                if map_pos > 0:
                    self.writeln(r'\vspace*{8ex}')
                    self.writeln(r'')

                image = cavedb.utils.get_region_gis_map(self.bulletin.id, region.id, map_name)

                self.writeln(r'\begin{figure}[htp!]')
                self.writeln(r'  \centering')
                self.writeln(r'  \includegraphics[height=0.9\textheight,width=\textwidth,' + \
                             r'keepaspectratio=true]{' + image + '}')
                self.writeln(r'\end{figure}')
                self.writeln(r'')

                if map_pos == 0:
                    self.writeln(r'\begin{figure}[htp!]')
                    self.writeln(r'  \centering')
                    self.writeln(r'  \includegraphics[width=\textwidth,keepaspectratio=true]{' + \
                                 r'../../gis_maps/legend.png}')
                    self.writeln(r'\end{figure}')
                    self.writeln(r'')

                if map_name in self.gis_map_labels:
                    self.writeln(r'\begin{center} { \footnotesize \textit{' + \
                                 self.gis_map_labels[map_name] + r'}} \end{center}')
                    self.writeln(r'') # TODO AFTER - remove
                    self.writeln(r'')

                self.writeln(r'')
                self.writeln(r'\clearpage')
                self.writeln(r'')


    def begin_region(self, region, gis_region_hash):
        self.writeln(r'\clearpage')
        self.writeln(r'\ifthenelse{\isodd{\value{page}}}{}{\hbox{}\newpage}')

        self.writeln(r'\chapter{' + region.region_name + '}')

        self.__show_region_gis_maps(region)

        self.writeln(r'\twocolumn')
        self.writeln(r'\setlength\parskip{1ex plus 0in minus 0in}')

        if region.introduction:
            self.writeln(r'\section*{Introduction} { ' + region.introduction + '}')
            self.writeln(r'')


    def end_region(self):
        # FIXME - show feature photos at end

        self.writeln(r'\onecolumn')


    def __show_document_header(self):
        draftstr = ',draft' if self.draft_mode else ''

        self.writeln(r'\documentclass[10pt,' + self.papersize + ',leqno,twoside,openany' + \
                     draftstr + ']{book}')
        self.writeln(r'\usepackage{etex}')
        self.writeln(r'\reserveinserts{200}')
        self.writeln(r'\usepackage[utf8]{inputenc}')
        self.writeln(r'\usepackage{amsmath,amssymb,amsfonts} % Typical maths resource packages')
        self.writeln(r'\usepackage{graphicx}                 % Packages to allow inclusion of graphics')
        self.writeln(r'\usepackage{multicol}                 % Multiple column support')
        self.writeln(r'\usepackage{fancyhdr} ')
        self.writeln(r'\usepackage{longtable} ')
        self.writeln(r'\usepackage{colortbl} ')
        self.writeln(r'\usepackage{helvet}')
        self.writeln(r'\usepackage{tikz}')
        self.writeln(r'\usepackage{hyphenat}')
        self.writeln(r'\usepackage{ifthen}')
        self.writeln(r'\usepackage{makeidx}')
        self.writeln(r'\usepackage[maxfloats=145]{morefloats}')
        self.writeln(r'')
        self.writeln(r'\tikzstyle{mybox} = [draw=black, fill=gray!20, rectangle, ' + \
                     r'rounded corners, inner sep=5pt, inner ysep=7pt]')
        self.writeln(r'')
        self.writeln(r'% Note: always include this package last')
        self.writeln(r'\usepackage[pdftitle={' + self.bulletin.bulletin_name + '},' + \
                     r'pdfauthor={' + self.bulletin.editors + '}, plainpages=false, ' + \
                     r'pdfpagelabels]{hyperref}')
        self.writeln(r'')
        self.writeln(r'\sloppy')
        self.writeln(r'\raggedbottom')
        self.writeln(r'\raggedcolumns')
        self.writeln(r'\hbadness=10000')
        self.writeln(r'\clubpenalty=10000')
        self.writeln(r'\widowpenalty=10000')
        self.writeln(r'')
        self.writeln(r'\renewcommand{\thefigure}{}')
        self.writeln(r'\renewcommand{\figurename}{}')
        self.writeln(r'')
        self.writeln(r'%\renewcommand{\familydefault}{\sfdefault} ')
        self.writeln(r'')
        self.writeln(r'\makeatletter')
        self.writeln(r'')
        self.writeln(r'\renewcommand{\l@chapter}{\@dottedtocline{1}{1.5em}{2.3em}}')
        self.writeln(r'')

        self.writeln(r'\renewcommand{\@makechapterhead}[1]{')
        self.writeln(r'\vspace*{10 pt}')
        self.writeln(r'{\bfseries\LARGE \begin{centering} \nohyphens{#1} \\ \end{centering} }')
        self.writeln(r'}')
        self.writeln(r'\renewcommand{\section}{\@startsection {section}{1}{0pt}')
        self.writeln(r'  {0ex}')
        self.writeln(r'  {1px}')
        self.writeln(r'  {\bf\Large}}')
        self.writeln(r'')
        self.writeln(r'\setlength{\abovecaptionskip}{0pt} ')
        self.writeln(r'\setlength{\belowcaptionskip}{2pt}')
        self.writeln(r'')
        self.writeln(r'\long\def\@makecaption#1#2{%')
        self.writeln(r'   \vskip\abovecaptionskip')
        self.writeln(r'   \hspace{0.05\linewidth}\begin{minipage}[t]{0.9\linewidth}\centering' + \
                     r'\footnotesize#2\par\end{minipage}\hspace{0.05\linewidth}')
        self.writeln(r'   \vskip\belowcaptionskip}')
        self.writeln(r'')
        self.writeln(r'\makeatother')
        self.writeln(r'')
        self.writeln(r'\setlength\voffset{0in}')
        self.writeln(r'\setlength\topmargin{-0.5in}')
        self.writeln(r'\setlength\headheight{0in}')
        self.writeln(r'\setlength\headsep{0in}')
        self.writeln(r'\setlength\topskip{0in}')
        self.writeln(r'')
        self.writeln(r'\setlength\hoffset{0in}')
        self.writeln(r'\setlength\oddsidemargin{-0.25in}')
        self.writeln(r'\setlength\evensidemargin{-0.25in}')
        self.writeln(r'\setlength\rightmargin{-0.25in}')
        self.writeln(r'\setlength\textwidth{7in}')
        self.writeln(r'\setlength\textheight{9.5in}')
        self.writeln(r'')
        self.writeln(r'\setlength\parindent{0.0in}')
        self.writeln(r'\setlength\parskip{1ex plus 0in minus 0in}')
        self.writeln(r'\setlength{\topsep}{0in plus 0in minus 0in}')
        self.writeln(r'')
        self.writeln(r'\pagestyle{fancy}')
        self.writeln(r'')
        self.writeln(r'\renewcommand{\sectionmark}[1]{\markright{ - #1}}')
        self.writeln(r'\renewcommand{\headrulewidth}{0.0pt}')
        self.writeln(r'\renewcommand{\footrulewidth}{0.4pt}')
        self.writeln(r'\fancyhead[LE,RO]{}')
        self.writeln(r'\fancyhead[LO,RE]{}')
        self.writeln(r'\fancyfoot[C]{}')
        self.writeln(r'')
        self.writeln(r'')
        self.writeln(r'% This is the header and footer for the preamble pages. It is changed later on')
        self.writeln(r'% when the document body is shown.')
        self.writeln(r'')
        self.writeln(r'\fancyfoot[LE,RO]{\thepage}')
        self.writeln(r'\fancyfoot[LO,RE]{\textit{' + self.bulletin.bulletin_name + '}}')
        self.writeln(r'')
        self.writeln(r'\fancypagestyle{plain}{')
        self.writeln(r'  \fancyfoot[LE,RO]{\thepage}')
        self.writeln(r'  \fancyfoot[LO,RE]{\textit{' + self.bulletin.bulletin_name + '}}')
        self.writeln(r'} ')
        self.writeln(r'')
        self.writeln(r'')
        self.writeln(r'\setcounter{topnumber}{4}')
        self.writeln(r'\setcounter{dbltopnumber}{2}')
        self.writeln(r'\setcounter{bottomnumber}{0}')
        self.writeln(r'\setcounter{totalnumber}{4}')
        self.writeln(r'')
        self.writeln(r'\renewcommand{\topfraction}{0.6}')
        self.writeln(r'\renewcommand{\bottomfraction}{0}')
        self.writeln(r'\renewcommand{\textfraction}{0.3}')
        self.writeln(r'\renewcommand{\floatpagefraction}{0.5}')
        self.writeln(r'\renewcommand{\dbltopfraction}{0.7}')
        self.writeln(r'\renewcommand{\dblfloatpagefraction}{0.7}')
        self.writeln(r'')
        self.writeln(r'\pagenumbering{roman}')
        self.writeln(r'\makeindex')
        self.writeln(r'')
        self.writeln(r'\begin{document}')

    def __show_title_page(self):
        self.writeln(r'')
        self.writeln(r'% ---- Title Page ----')
        self.writeln(r'')
        self.writeln(r'\clearpage')
        self.writeln(r'\thispagestyle{empty}')
        self.writeln(escape(self.generate_index(self.bulletin.title_page.strip())))
        self.writeln(r'\newpage')
        self.writeln(r'')


    def __show_preamble_page(self):
        self.writeln(r'')
        self.writeln(r'\clearpage')
        self.writeln(r'\thispagestyle{empty}')
        self.writeln(escape(self.generate_index(self.bulletin.preamble_page.strip())))
        self.writeln(r'\newpage')
        self.writeln(r'')


    def __show_contributor_page(self):
        self.writeln(r'')
        self.writeln(r'\clearpage')
        self.writeln(escape(self.generate_index(self.bulletin.contributor_page.strip())))
        self.writeln(r'\newpage')
        self.writeln(r'')


    def __show_toc(self):
        self.writeln(r'')
        self.writeln(r'\clearpage')
        self.writeln(r'\tableofcontents')
        self.writeln(r'\clearpage')
        self.writeln(r'')

        if self.bulletin.toc_footer:
            self.writeln(escape(self.generate_index(self.bulletin.toc_footer.strip())))

        self.writeln(r'')


    def get_bw_gis_map_names(self):
        ret = []

        if self.bulletin.bw_map1:
            ret.append(self.bulletin.bw_map1)
        if self.bulletin.bw_map2:
            ret.append(self.bulletin.bw_map2)
        if self.bulletin.bw_map3:
            ret.append(self.bulletin.bw_map3)

        return ret


    def get_color_gis_map_names(self):
        ret = []

        if self.bulletin.color_map1:
            ret.append(self.bulletin.color_map1)
        if self.bulletin.color_map2:
            ret.append(self.bulletin.color_map2)
        if self.bulletin.color_map3:
            ret.append(self.bulletin.color_map3)

        return ret


    # Note: You must override this method in a subclass
    def get_gis_map_names(self):
        return None

    def write(self, line):
        line = line.replace('/usr/local/cavedbmanager-data/bulletins/bulletin_1', '.') # TODO AFTER - remove
        self.file_handle.write(line.replace('\r', ''))


    def writeln(self, line):
        self.write(line + '\n')


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

        # FIXME - check for features added to the end of the region
        self.feature_attrs['photos'].append(photo)


    def feature_referenced_map(self, feature, refmap):
        self.feature_attrs['refmaps'].append(refmap)


    def feature_reference(self, feature, ref):
        self.feature_attrs['refs'].append(ref)


    def __feature_names(self, feature):
        self.writeln(r'\begin{centering}')

        self.writeln(r'{\Large \bfseries \uppercase{' + escape(feature.name) + r'} } \\*')

        alt_names = comma_split(feature.alternate_names)
        if len(alt_names) > 0:
            self.writeln(r'{\large \bfseries (' + ', '.join(alt_names) + r')} \\[2ex]')

        self.writeln(r'\end{centering}')


    def __feature_length_and_depth(self, feature):
        if not feature.length_ft or feature.length_ft <= 0:
            return

        approx = r'$\sim$' if feature.length_based_on == 'estimate' else ''

        if feature.length_ft < 5280:
            length_str = '{:,} ft'.format(feature.length_ft)
        else:
            length_str = '{:,} mi'.format(round(feature.length_ft / 5280.0, 1))

        self.write(r'Length: %s%s' % (approx, length_str))

        if feature.depth_ft:
            depth_str = '{:,} ft'.format(feature.depth_ft)

            self.write(r' \hfill Depth: %s%s' % (approx, depth_str))

        self.writeln(r' \\*')


    def __decimal_degrees_to_ddmmss_str(self, decdegs):
        positive = decdegs >= 0
        mins, secs = divmod(abs(decdegs) * 3600, 60)
        degs, mins = divmod(mins, 60)
        degs = degs if positive else -degs

        return '%.0f$^\\circ$ %02d\' %s"' % (degs, mins, ('%.1f' % (secs)).zfill(4))


    def __show_coordinates(self, entrance, coordinates):
        hemisphere = 'N ' if coordinates.utmzone.utm_north else 'S '
        self.writeln(r'NAD27 UTM: \hfill ' + str(coordinates.utmzone.utm_zone) + hemisphere + \
                     '%.0f' % (coordinates.nad27_utmnorth) + r'N ' + \
                     '%.0f' % (coordinates.nad27_utmeast) + r'E \\*')

        self.writeln(r'WGS84 Lat/Lon: \hfill ' + \
                     self.__decimal_degrees_to_ddmmss_str(coordinates.wgs84_lat) + r' / ' + \
                     self.__decimal_degrees_to_ddmmss_str(coordinates.wgs84_lon) + r' \\*')

        if entrance.elevation_ft:
            self.write('Elevation: {:,}'.format(entrance.elevation_ft) + '\'')
        if entrance.quad:
            self.write(r' \hfill ' + entrance.quad.quad_name + r' Quad')
        if entrance.elevation_ft or entrance.quad:
            self.writeln(r' \\*')

        if entrance.coord_acquision == 'GPS':
            self.writeln(r'\textit{Coordinates acquired using a GPS receiver.} \\*')
        elif entrance.coord_acquision == 'Other Topo Map':
            self.writeln(r'\textit{Coordinates acquired off of a topo map.} \\*')
        elif entrance.coord_acquision == '7.5 Topo Map':
            self.writeln(r'\textit{Coordinates acquired off of a 7.5\' topo map.} \\*')
        elif entrance.coord_acquision == 'Google Earth':
            self.writeln(r'\textit{Coordinates acquired using Google Earth.} \\*')
        elif entrance.coord_acquision == 'Estimate':
            self.writeln(r'\textit{Coordinates are an estimate.} \\*')
        elif entrance.coord_acquision == 'Filled In':
            self.writeln(r'\textit{Entrance is filled in; coordinates are an estimate.} \\*')
        else:
            # TODO AFTER - change message
            #self.writeln(r'\textit{Unknown coordinate acquisition method.} \\*')
            self.writeln(r'\textit{Coordinates acquired off of a topo map.} \\*')


    def __show_feature_header(self, feature):
        self.writeln(r'\vspace{1ex}')
        self.writeln(r'')
        self.writeln(r'\begin{tikzpicture}')
        self.writeln(r'\node [mybox] (box){')
        self.writeln(r'\begin{minipage}[b]{0.95\columnwidth}')
        self.writeln(r'\phantomsection')
        self.writeln(r'\label{feature' + str(feature.id) + r'}')

        self.__feature_names(feature)

        self.__feature_length_and_depth(feature)

        has_coordinates = False
        for counter, (entrance, coordinates) in enumerate(self.feature_attrs['entrances']):
            if counter > 0:
                self.writeln(r' \\')

            if entrance.entrance_name and entrance.entrance_name != feature.name:
                self.writeln(r'\textit{\textbf{' + escape(entrance.entrance_name) + r'}} \\*')

            if coordinates.wgs84_lat:
                has_coordinates = True
                self.__show_coordinates(entrance, coordinates)

        if not has_coordinates:
            self.writeln(r'\textit{Coordinates are not available.} \\*')

        self.writeln(r'\vspace{-2ex}')
        self.writeln(r'\end{minipage}')
        self.writeln(r'};')
        self.writeln(r'\index{' + escape(feature.name) + '|(}')
        self.writeln(r'\end{tikzpicture}')
        self.writeln(r'\nopagebreak[4]')


    def __show_feature_body(self, feature):
        self.write_paragraphs('\n{ \\bf ', feature.hazards, ' }\n\n')

        if not self.write_paragraphs(None, feature.description, None):
            self.writeln('There is currently no description available.\n')

        self.write_paragraphs('\n\n', feature.geology_hydrology, None)

        self.write_paragraphs('\n\n{ \\bf Biology:} ', feature.biology, None)

        self.write_paragraphs('\n\n{ \\bf History:} ', feature.history, None)

        if feature.source:
            self.write(r' \textit{(' + feature.source + r')}')

        self.writeln(r'')
        self.writeln(r'')

        self.__show_references(self.feature_attrs['refs'])

        self.writeln(r'\index{' + escape(feature.name) + r'|)}')


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

        for alias in get_all_feature_alt_names(feature):
            see_label = alias + r'\begin{description}' + '\n' + \
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


    def get_bw_photo_filename(self, photo):
        if photo.filename:
            return photo.filename.path

        return photo.secondary_filename.path


    def get_color_photo_filename(self, photo):
        if photo.secondary_filename:
            return photo.secondary_filename.path

        return photo.filename.path


    # Note: You must override this method in a subclass
    def get_photo_filename(self, photo):
        return None


    def __show_feature_photo(self, feature, photo):
        if self.num_in_pdf % 48 == 0:
            self.writeln(r'\clearpage')

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

        self.writeln(r'\begin{figure' + figure_opts + '}[tp]')
        self.writeln(r'\phantomsection')

        self.writeln(r'\index{' + escape(feature.name) + '}')
        # TODO AFTER - uncomment
        #for alias in get_all_feature_alt_names(feature):
        #    self.writeln(r'\index{' + escape(alias) + '}')

        self.writeln(r'\centering')

        url = self.get_photo_filename(photo)
        self.writeln(r'  \includegraphics[' + graphic_opts + r']{' + url + r'}')

        if photo.caption:
            # TODO AFTER - add extra space
            self.writeln(r' \caption{' + self.format_photo_caption(feature, photo.caption) + r'}')

        self.writeln(r'  \label{photo' + str(photo.id) + r'}')
        self.writeln(r'\end{figure' + figure_opts + '}')

        self.writeln(r'')
        self.writeln(r'')

        if photo.type != 'map':
            self.list_of_photos.append(r'\pageref{photo' + str(photo.id) + r'}  & ' + \
                                       escape(feature.name) + r' & ' +
                                       escape(photo.people_shown) + r' & ' + \
                                       escape(photo.author) + r' \\')


    def format_photo_caption(self, feature, caption):
        caption = add_caption_hbox(caption, feature.name)

        for alias in get_all_feature_alt_names(feature):
            caption = add_caption_hbox(caption, alias)

        for (entrance, coordinates) in self.feature_attrs['entrances']:
            if entrance.entrance_name:
                caption = add_caption_hbox(caption, entrance.entrance_name)

        return escape(caption)


    def __show_references(self, refs):
        if len(refs) == 0:
            return

        self.writeln(r'{ \footnotesize')
        self.writeln(r'\leftskip 0.2in')
        self.writeln(r'\parindent -0.1in')

        # FIXME - sort references
        # <xsl:sort select="@parsed_date"/>
        # <xsl:sort select="@volume" data-type="number"/>
        # <xsl:sort select="@number" data-type="number"/>
        # <xsl:sort select="@pages" data-type="number"/>
        # <xsl:sort select="@book"/>
        # <xsl:sort select="@title"/>

        num_refs = len(refs)

        # Sort the references by date
        refs_by_date = {}
        for ref in refs:
            parsed_date = get_normalized_date(ref.date) + none_to_empty(ref.volume) + \
                          none_to_empty(ref.number) + none_to_empty(ref.pages) + \
                          none_to_empty(ref.book) + none_to_empty(ref.title)

            if parsed_date not in refs_by_date:
                refs_by_date[parsed_date] = []

            refs_by_date[parsed_date].append(ref)

        counter = 0
        for parsed_date in sorted(refs_by_date):
            for ref in refs_by_date[parsed_date]:
                counter = counter + 1

                if counter < 3 or counter % 2 == 0 or counter == num_refs:
                    self.writeln(r'\nopagebreak[4]')

                if counter > 1:
                    self.writeln(r'\vspace{-3.5ex}')

                self.__show_reference(ref)

        self.writeln('}')

        self.writeln(r'')
        self.writeln(r'')


    def __show_book_bibliography(self):
        self.writeln(r'\chapter{Bibliography}')
        self.writeln(r'\begin{multicols}{2}')
        self.writeln(r'{ ')
        self.writeln(r'\setlength{\parskip}{-2ex plus 0in minus 0in}')
        self.writeln(r'\parindent -0.1in')
        self.writeln(r'\leftskip 0.2in')
        self.writeln(r'\it')
        self.writeln(r'\footnotesize')

        # hidden_in_bibliography = ref.title.startswith('unpublished trip report') or \
        #                          ref.title.startswith('Tucker County Speleological Survey Files') or \
        #                          ref.title.startswith('personal communication') or \
        #                          ref.title.startswith('e-mail') or \
        #                          ref.title.startswith('letter to') or \
        #                          ref.title.startswith('Trip Report in NSS Files')

        # FIXME - show all references
        #  <xsl:for-each select="/regions/all_references/reference[@hidden_in_bibliography='False' and generate-id() = generate-id(key('distinctRefs', concat(@author, @title, @book, @volume, @number, @pages, @url, @date, @extra)))]">
        # <xsl:sort select="@author"/>
        # <xsl:sort select="@parsed_date"/>
        # <xsl:sort select="@volume" data-type="number"/>
        # <xsl:sort select="@number" data-type="number"/>
        # <xsl:sort select="@pages" data-type="number"/>
        # <xsl:sort select="@book"/>
        # <xsl:sort select="@title"/>

        self.writeln(r'')
        self.writeln(r'}')
        self.writeln(r'\end{multicols}')


    def __show_list_of_photos(self):
        self.writeln(r'\chapter{List of Photos}')
        self.writeln(r'\begin{center}')
        self.writeln(r'\begin{longtable}{|c| p{5cm} | p{5cm} | p{5cm} |}')
        self.writeln(r'    %This is the header for the first page of the table...')
        self.writeln(r'    \hline')
        self.writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Page & Cave & People Shown In Photo & Photographer \\')
        self.writeln(r'    \hline')
        self.writeln(r'  \endfirsthead')
        self.writeln(r'')
        self.writeln(r'    %This is the header for the remaining page(s) of the table...')
        self.writeln(r'    \hline')
        self.writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Page & Cave & People Shown In Photo & Photographer \\')
        self.writeln(r'    \hline')
        self.writeln(r'  \endhead')
        self.writeln(r'')
        self.writeln(r'    %This is the footer for all pages except the last page of the table...')
        self.writeln(r'    \hline')
        self.writeln(r'  \endfoot')
        self.writeln(r'')
        self.writeln(r'    %This is the footer for the last page of the table...')
        self.writeln(r'    \hline ')
        self.writeln(r'  \endlastfoot')

        if self.bulletin.photo_index_header:
            self.writeln(escape(self.bulletin.photo_index_header))

        for counter, photo in enumerate(self.list_of_photos):
            if counter % 2 != 0:
                self.write(r'\rowcolor[rgb]{0.95,0.95,0.95} ')

            self.writeln(photo)
            self.write('  ') # TODO AFTER - remove

        self.writeln(r'\end{longtable}')
        self.writeln(r'\end{center}')


    def __show_list_of_caves(self):
        self.writeln(r'\chapter{Index of Caves}')
        self.writeln(r'\begin{center}')
        self.writeln(r'\begin{longtable}{| p{5.5cm} |c|c|c|c|c|c|c|}')
        self.writeln(r'    %This is the header for the first page of the table...')
        self.writeln(r'    \hline')
        self.writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Name & ID & Type & Length & Depth & Page & Map & Ent. \\')
        self.writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} & & & & & & & Photo \\')
        self.writeln(r'    \hline')
        self.writeln(r'  \endfirsthead')
        self.writeln(r'')
        self.writeln(r'    %This is the header for the remaining page(s) of the table...')
        self.writeln(r'    \hline')
        self.writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} \centering Name & ID & Type & Length & Depth & Page & Map & Ent. \\')
        self.writeln(r'    \rowcolor[rgb]{0.9,0.9,0.9} & & & & & & & Photo \\')
        self.writeln(r'    \hline')
        self.writeln(r'  \endhead')
        self.writeln(r'')
        self.writeln(r'    %This is the footer for all pages except the last page of the table...')
        self.writeln(r'    \hline')
        self.writeln(r'  \endfoot')
        self.writeln(r'')
        self.writeln(r'    %This is the footer for the last page of the table...')
        self.writeln(r'    \hline')
        self.writeln(r'  \endlastfoot')

        self.list_of_caves.sort()
        for counter, cave in enumerate(self.list_of_caves):
            if counter % 2 != 0:
                self.write(r'\rowcolor[rgb]{0.95,0.95,0.95} ')

            self.writeln(cave)

        self.writeln(r'\end{longtable}')
        self.writeln(r'\end{center}')


    def __show_reference(self, ref):
        parts = []
        if ref.author:
            parts.append(escape(ref.author))

        if ref.title:
            parts.append(escape(ref.title))

        if ref.book:
            parts.append(r'\textnormal{``' + escape(ref.book) + '\'\'}')

        if ref.volume:
            vnp = r'V' + escape(ref.volume)

            if ref.number:
                vnp = vnp + r'n' + escape(ref.number)

            if ref.pages:
                vnp = vnp + r'p'
                if '-' in ref.pages or ',' in ref.pages:
                    vnp = vnp + r'p'
                vnp += escape(ref.pages)

            if vnp:
                parts.append(vnp)

        if ref.url:
            parts.append(r'URL: ' + escape(ref.url))

        if ref.extra:
            parts.append(escape(ref.extra))

        if ref.date:
            parts.append(escape(ref.date))
        else:
            parts.append('date unknown')

        if not ref.volume and ref.pages:
            if '-' in ref.pages or ',' in ref.pages:
                parts.append('Pages ' + escape(ref.pages))
            else:
                parts.append('Page ' + escape(ref.pages))

        self.writeln(r'\textit{' + ', '.join(parts) + r'} \\')
        self.writeln(r'')


    def write_chapters(self, is_appendix):
        for chapter in cavedb.models.BulletinChapter.objects.filter(bulletin__id=self.bulletin.id):
            if chapter.is_appendix != is_appendix:
                continue

            self.writeln(r'\chapter{' + escape(chapter.chapter_title) + r'}')

            for section in cavedb.models.BulletinSection.objects \
               .filter(bulletin_chapter__id=chapter.id):

                if section.section_title:
                    self.writeln(r'\section{' + escape(section.section_title) + r'}')

                if section.section_subtitle:
                    self.writeln(r'{\begin{centering} \small \textit{' + \
                                 escape(section.section_subtitle) + r'} \\* \end{centering} }')

                if section.num_columns > 1:
                    self.writeln(r'\begin{multicols}{2}')

                self.writeln(r'\parindent 2ex')

                self.writeln(escape(section.section_data))
                self.writeln(r'')

                self.writeln(r'\parindent 0ex')

                refs = []
                for ref in cavedb.models.BulletinSectionReference.objects \
                   .filter(bulletinsection__id=section.id):
                    refs.append(ref)

                self.__show_references(refs)

                if section.num_columns > 1:
                    self.writeln(r'\end{multicols}')


    def write_paragraphs(self, prefix, inputstr, suffix):
        if not inputstr:
            return False

        first_para = True
        for para in inputstr.strip().split('\n'):
            para = para.replace('\r', '')
            para = para.replace('\n', '')
            if not para:
                continue

            if first_para:
                if prefix:
                    self.write(prefix)
                first_para = False
            else:
                self.writeln(r'')
                self.writeln(r'')

            self.write(escape(self.generate_index(para)))

        if not first_para:
            if suffix:
                self.write(suffix)

        # Return whether or not paragraphs were shown.
        return not first_para


    def get_indexed_terms(self):
        indexed_terms = [], {}
        if self.bulletin.indexed_terms:
            for search_term in self.bulletin.indexed_terms.split('\n'):
                search_term = escape(search_term.replace('\r', '').strip())
                if not search_term:
                    continue

                all_index_terms = search_term.split(':')
                if len(all_index_terms) == 1:
                    indexed_terms[0].append(search_term)
                    indexed_terms[1][search_term] = r'\index{%s}%s' % (search_term, search_term)
                else:
                    replacement = ''
                    for index_term in all_index_terms[1:]:
                        replacement = r'%s\index{%s}' % (replacement, index_term)
                    indexed_terms[0].append(all_index_terms[0])
                    indexed_terms[1][all_index_terms[0]] = '%s%s' % \
                       (replacement, all_index_terms[0])

        for region in cavedb.models.BulletinRegion.objects.filter(bulletin__id=self.bulletin.id):
            for feature in cavedb.models.Feature.objects.filter(bulletin_region__id=region.id):
                feature_name = feature.name.strip()
                indexed_terms[0].append(feature_name)
                indexed_terms[1][feature_name] = r'\index{%s}%s' % (feature_name, feature_name)

                for alias in get_all_feature_alt_names(feature):
                    indexed_terms[0].append(alias)
                    indexed_terms[1][alias] = r'\index{%s}%s' % (alias, alias)

        indexed_terms[0].sort(key=lambda term: len(term), reverse=True)

        return indexed_terms


    def clean_index(self, inputstr):
        # FIXME - ugly hack for Tucker County
        inputstr = inputstr.replace(r"\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of Cheat River}", \
                                    r"\caveindex{Great Cave of Dry Fork of Cheat River}")
        inputstr = inputstr.replace(r"\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of \caveindex{Cheat River}}", \
                                    r"\caveindex{Great Cave of Dry Fork of Cheat River}")

        flags = re.MULTILINE | re.DOTALL | re.VERBOSE
        result = re.compile(r'(.*?)(\\caveindex{)(.*?)}(.*)', flags).match(inputstr)
        if not result:
            return inputstr
        elif re.compile(r'^\\caveindex{.*', flags).match(result.group(3)):
            value = re.sub(r'^\\caveindex{', '', result.group(3))
            return '%s%s%s%s' % (result.group(1), result.group(2), value, \
                                 self.clean_index(result.group(4)))
        elif not re.compile(r'^.*\\caveindex.*$', flags).match(result.group(3)):
            if re.compile(r'^.*\\caveindex.*$', flags).match(result.group(4)):
                return '%s%s%s}%s' % (result.group(1), result.group(2), result.group(3), \
                                      self.clean_index(result.group(4)))
            else:
                return inputstr
        else:
            value = re.sub(r'^(.*?)\s\\caveindex{(.*)', r'\1 \2', result.group(3))
            return '%s%s' % (result.group(1),
                             self.clean_index('%s%s%s' % (result.group(2), value, result.group(4))))


    def finalize_index(self, inputstr):
        flags = re.MULTILINE | re.DOTALL | re.VERBOSE
        result = re.compile(r'(.*?)\\caveindex{(.*?)}(.*)', flags).match(inputstr)
        if not result:
            return inputstr

        return '%s%s%s' % (result.group(1), self.indexed_terms[1][result.group(2)], \
                           self.finalize_index(result.group(3)))


    def generate_index(self, inputstr):
        # Add terms to the index
        for term in self.indexed_terms[0]:
            # This appears to be quicker than doing a single regular expression
            inputstr = inputstr.replace('%s ' % (term), r'\caveindex{%s} ' % (term))
            inputstr = inputstr.replace('%s.' % (term), r'\caveindex{%s}.' % (term))
            inputstr = inputstr.replace('%s,' % (term), r'\caveindex{%s},' % (term))
            inputstr = inputstr.replace('%s:' % (term), r'\caveindex{%s}:' % (term))
            inputstr = inputstr.replace('%s)' % (term), r'\caveindex{%s})' % (term))
            inputstr = inputstr.replace('%s\'' % (term), r'\caveindex{%s}\'' % (term))

        return self.finalize_index(self.clean_index(inputstr))


# Add a \hbox{} around the cave and entrance names so that they appear on the
# same line in the PDF.
def add_caption_hbox(caption, name):
    if caption.startswith(name):
        return caption

    return caption.replace(name, r'\hbox{%s}' % (name))


def escape(inputstr):
    if not inputstr:
        return ""

    inputstr = inputstr.strip()

    # Escape the # for LaTeX
    inputstr = inputstr.replace('#', '\\#')

    # Use em dashes
    inputstr = inputstr.replace(" - ", " -- ")

    # Use the directional quotes
    while True:
        if inputstr.count("\"") < 2:
            break

        inputstr = inputstr.replace("\"", "``", 1)
        inputstr = inputstr.replace("\"", "''", 1)

    return inputstr


def get_normalized_date(datestr):
    # Parse different date formats including:
    # Sep 21, 1997, Fall/Winter 1997, Fall 1997, etc.

    if not datestr:
        return "0000-00-00"

    pattern = re.compile(r'/[\w\d]+')
    datestr = pattern.sub('', datestr)

    datestr = datestr.replace("Spring", "April")
    datestr = datestr.replace("Summer", "July")
    datestr = datestr.replace("Fall", "October")
    datestr = datestr.replace("Winter", "January")

    try:
        defaults = datetime.datetime.now() + \
                   dateutil.relativedelta.relativedelta(month=1, day=1, hour=0, minute=0, \
                                                        second=0, microsecond=0)
        return dateutil.parser.parse(datestr, default=defaults).strftime("%Y-%m-%d")
    except ValueError:
        return "0000-00-00"


def get_all_feature_alt_names(feature):
    alternate_names = comma_split(feature.alternate_names)
    additional_index_names = comma_split(feature.additional_index_names)

    return alternate_names + additional_index_names


def comma_split(inputstr):
    ret = []

    if not inputstr:
        return ret

    for member in inputstr.split(','):
        member = member.strip()
        if not member:
            continue

        ret.append(member)

    return ret


def none_to_empty(inputstr):
    return inputstr if inputstr else ''

