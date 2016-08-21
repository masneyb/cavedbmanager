<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY nbsp "&#160;">
<!ENTITY quot "&#34;">
<!ENTITY deg  "&#176;">
]>

<!-- This stylesheet will generate a LaTeX file for the cave portion of the
     bulletin. I'm sorry the whitespace is so messy in this file. It has to be
     that way so that the proper LaTeX file will be generated. 
          - Brian Masney 
  -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:param name="gis_output_dir"/>
  <xsl:param name="feature_photo"/>
  <xsl:param name="draft_mode"/>
  <xsl:param name="bulletin_type"/>

  <xsl:output method="text" indent="no" encoding="US-ASCII"/>
  <xsl:strip-space elements="*"/>

  <xsl:key name="distinctRefs" match="/regions/all_references/reference" use="concat(@author, @title, @book, @volume, @number, @pages, @url, @date, @extra)"/>

  <xsl:template match="/regions">
    <xsl:call-template name="show_document_header"/>
    <xsl:call-template name="show_title_page"/>
    <xsl:call-template name="show_preamble_page"/>
    <xsl:call-template name="show_contributor_page"/>
    <xsl:call-template name="show_toc"/>
    <xsl:call-template name="show_document_body"/>
    <xsl:apply-templates select="." mode="bibliography"/>
    <xsl:apply-templates select="." mode="photos_index"/>
    <xsl:apply-templates select="." mode="caves_index"/>

    <xsl:text>

% Change the header and footer for the index
\fancyfoot[LO,RE]{\thepage}
\fancyfoot[LE,RO]{\textit{</xsl:text> <xsl:value-of select="/regions/@name"/> <xsl:text> \\ \nouppercase\leftmark}}

\fancypagestyle{plain}{
  \fancyfoot[LO,RE]{\thepage}
  \fancyfoot[LE,RO]{\textit{</xsl:text> <xsl:value-of select="/regions/@name"/> <xsl:text>}}
}

\printindex
</xsl:text>

    <xsl:call-template name="show_document_footer"/>
  </xsl:template>

<!-- *********************************************************************** -->
<!-- ** Misc functions                                                    ** -->
<!-- *********************************************************************** -->

<xsl:template name="abs">
  <xsl:param name="num"/>
  <xsl:value-of select="(1 - 2 * ($num &lt; 0)) * $num"/>
</xsl:template>

<xsl:template name="convert_to_ddmmss">
  <xsl:param name="dec_degrees"/>

  <xsl:variable name="abs_dec_degrees">
    <xsl:call-template name="abs">
      <xsl:with-param name="num"><xsl:value-of select="$dec_degrees"/></xsl:with-param>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="degrees"><xsl:number value="$abs_dec_degrees"/></xsl:variable>
  <xsl:variable name="dec_minutes"><xsl:value-of select="($abs_dec_degrees - $degrees) * 60"/></xsl:variable>
  <xsl:variable name="minutes"><xsl:number value="$dec_minutes"/></xsl:variable>
  <xsl:variable name="dec_seconds"><xsl:value-of select="format-number(($dec_minutes - $minutes) * 60, '00.0')"/></xsl:variable>

  <xsl:if test="$dec_degrees &lt; 0">
    <xsl:text>-</xsl:text>
  </xsl:if>

  <xsl:value-of select="$degrees"/>
  <xsl:text>$^\circ$ </xsl:text>
  <xsl:value-of select="format-number($minutes, '00')"/>
  <xsl:text>' </xsl:text>
  <xsl:value-of select="format-number($dec_seconds, '00.0')"/>
  <xsl:text>"</xsl:text>
</xsl:template>

<!-- *********************************************************************** -->
<!-- ** Document header                                                   ** -->
<!-- *********************************************************************** -->

<xsl:template name="show_document_header">
<xsl:text>\documentclass[10pt,letterpaper,leqno,twoside,openany</xsl:text>
<xsl:if test="$draft_mode='1'">
  <xsl:text>,draft</xsl:text>
</xsl:if>
<xsl:text>]{book}
\usepackage{etex}
\reserveinserts{200}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsfonts} % Typical maths resource packages
\usepackage{graphicx}                 % Packages to allow inclusion of graphics
\usepackage{multicol}                 % Multiple column support
\usepackage{fancyhdr} 
\usepackage{longtable} 
\usepackage{colortbl} 
\usepackage{helvet}
\usepackage{tikz}
\usepackage{hyphenat}
\usepackage{ifthen}
\usepackage{makeidx}
\usepackage[maxfloats=145]{morefloats}

\tikzstyle{mybox} = [draw=black, fill=gray!20, rectangle, rounded corners, inner sep=5pt, inner ysep=7pt]

% Note: always include this package last
\usepackage[pdftitle={</xsl:text>
<xsl:value-of select="/regions/@name"/>
<xsl:text>},pdfauthor={</xsl:text>
<xsl:value-of select="/regions/@editors"/>
<xsl:text>}, plainpages=false, pdfpagelabels]{hyperref}

\sloppy
\raggedbottom
\raggedcolumns
\hbadness=10000
\clubpenalty=10000
\widowpenalty=10000

\renewcommand{\thefigure}{}
\renewcommand{\figurename}{}

%\renewcommand{\familydefault}{\sfdefault} 

\makeatletter

\renewcommand{\l@chapter}{\@dottedtocline{1}{1.5em}{2.3em}}

\renewcommand{\@makechapterhead}[1]{
\vspace*{10 pt}
{\bfseries\LARGE \begin{centering} \nohyphens{#1} \\ \end{centering} }
}
\renewcommand{\section}{\@startsection {section}{1}{0pt}
  {0ex}
  {1px}
  {\bf\Large}}

\setlength{\abovecaptionskip}{0pt} 
\setlength{\belowcaptionskip}{2pt}

\long\def\@makecaption#1#2{%
   \vskip\abovecaptionskip
   \hspace{0.05\linewidth}\begin{minipage}[t]{0.9\linewidth}\centering\footnotesize#2\par\end{minipage}\hspace{0.05\linewidth}
   \vskip\belowcaptionskip}

\makeatother

\setlength\voffset{0in}
\setlength\topmargin{-0.5in}
\setlength\headheight{0in}
\setlength\headsep{0in}
\setlength\topskip{0in}

\setlength\hoffset{0in}
\setlength\oddsidemargin{-0.25in}
\setlength\evensidemargin{-0.25in}
\setlength\rightmargin{-0.25in}
\setlength\textwidth{7in}
\setlength\textheight{9.5in}

\setlength\parindent{0.0in}
\setlength\parskip{1ex plus 0in minus 0in}
\setlength{\topsep}{0in plus 0in minus 0in}

\pagestyle{fancy}

\renewcommand{\sectionmark}[1]{\markright{ - #1}}
\renewcommand{\headrulewidth}{0.0pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyhead[LE,RO]{}
\fancyhead[LO,RE]{}
\fancyfoot[C]{}


% This is the header and footer for the preamble pages. It is changed later on
% when the document body is shown.

\fancyfoot[LE,RO]{\thepage}
\fancyfoot[LO,RE]{\textit{</xsl:text> <xsl:value-of select="/regions/@name"/> <xsl:text>}}

\fancypagestyle{plain}{
  \fancyfoot[LE,RO]{\thepage}
  \fancyfoot[LO,RE]{\textit{</xsl:text> <xsl:value-of select="/regions/@name"/> <xsl:text>}}
} 


\setcounter{topnumber}{4}
\setcounter{dbltopnumber}{2}
\setcounter{bottomnumber}{0}
\setcounter{totalnumber}{4}

\renewcommand{\topfraction}{0.6}
\renewcommand{\bottomfraction}{0}
\renewcommand{\textfraction}{0.3}
\renewcommand{\floatpagefraction}{0.5}
\renewcommand{\dbltopfraction}{0.7}
\renewcommand{\dblfloatpagefraction}{0.7}

\pagenumbering{roman}
\makeindex

\begin{document}

% ---- Title Page ----
</xsl:text>

</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Preamble and title pages                                          ** -->
<!-- *********************************************************************** -->

<xsl:template name="show_title_page">
  <xsl:text>
\clearpage
\thispagestyle{empty}
</xsl:text>
  <xsl:value-of select="/regions/title_page"/>
  <xsl:text>\newpage

</xsl:text>
</xsl:template>

<xsl:template name="show_preamble_page">
  <xsl:text>
\clearpage
\thispagestyle{empty}
</xsl:text>
  <xsl:value-of select="/regions/preamble_page"/>
  <xsl:text>\newpage

</xsl:text>
</xsl:template>

<xsl:template name="show_contributor_page">
  <xsl:text>
\clearpage
</xsl:text>
  <xsl:value-of select="/regions/contributor_page"/>
  <xsl:text>\newpage

</xsl:text>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Table of contents                                                 ** -->
<!-- *********************************************************************** -->

<xsl:template name="show_toc">
  <xsl:text>\clearpage
\tableofcontents
\clearpage

</xsl:text>

  <xsl:if test="/regions/toc_footer != ''">
    <xsl:value-of select="/regions/toc_footer"/>
  </xsl:if>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Document body                                                     ** -->
<!-- *********************************************************************** -->

<xsl:template match="/regions/chapters/chapter">
  <xsl:text>\chapter{</xsl:text>
  <xsl:value-of select="@title"/>
  <xsl:text>}
</xsl:text>

  <xsl:for-each select="section">
    <xsl:if test="@title">
      <xsl:text>\section{</xsl:text>
      <xsl:value-of select="@title"/>
      <xsl:text>}
</xsl:text>
    </xsl:if>

    <xsl:if test="@subtitle">
      <xsl:text>{\begin{centering} \small \textit{</xsl:text>
      <xsl:value-of select="@subtitle"/>
      <xsl:text>} \\* \end{centering} }
</xsl:text>
    </xsl:if>

    <xsl:if test="text/@num_columns > 1">
      <xsl:text>\begin{multicols}{2}
</xsl:text>
    </xsl:if>

    <xsl:text>\parindent 2ex
</xsl:text>
    <xsl:value-of select="text"/>
    <xsl:text>

</xsl:text>
    <xsl:text>\parindent 0ex
</xsl:text>

    <xsl:call-template name="show_references"/>

    <xsl:if test="text/@num_columns > 1">
      <xsl:text>\end{multicols}
</xsl:text>
    </xsl:if>
  </xsl:for-each>
</xsl:template>


<xsl:template match="/regions/region" mode="index">
  <xsl:param name="suffix"/>

  <!-- FIXME _ broken for Grant County <xsl:for-each select="features/feature">
    <xsl:text>\index{</xsl:text>
    <xsl:value-of select="name"/>
    <xsl:value-of select="$suffix"/>
    <xsl:text>}</xsl:text>
  </xsl:for-each>
  <xsl:text>
</xsl:text>-->
</xsl:template>


<xsl:template name="show_document_body">
  <xsl:text>\newpage
\pagenumbering{arabic}


% Change the header and footer for the document body
\fancyfoot[LO,RE]{\thepage}
\fancyfoot[LE,RO]{\textit{</xsl:text> <xsl:value-of select="/regions/@name"/> <xsl:text> \\ \nouppercase\leftmark \nouppercase\rightmark}}

\fancypagestyle{plain}{
  \fancyfoot[LO,RE]{\thepage}
  \fancyfoot[LE,RO]{\textit{</xsl:text> <xsl:value-of select="/regions/@name"/> <xsl:text>}}
} 


</xsl:text>

  <!-- ################################ -->
  <!-- Show the introduction if present -->
  <!-- ################################ -->

  <xsl:if test="caves_header != ''">
    <xsl:text>\chapter{Introduction}
\begin{multicols}{2}
\parindent 2ex
</xsl:text>

    <xsl:value-of select="caves_header"/>

    <xsl:text>\parindent 0ex
\end{multicols}
</xsl:text>
  </xsl:if>

  <xsl:text>\clearpage
</xsl:text>


  <!-- ########################## -->
  <!-- Show the embedded chapters -->
  <!-- ########################## -->

  <xsl:apply-templates select="chapters/chapter[@is_appendix='0']"/>

  <xsl:for-each select="region">
    <xsl:text>\clearpage
\ifthenelse{\isodd{\value{page}}}{}{\hbox{}\newpage}
</xsl:text>

    <xsl:text>\chapter{</xsl:text>
    <xsl:value-of select="@name"/>
    <xsl:text>}
</xsl:text>

    <xsl:if test="@show_gis_map='1' and features/feature/location[@utm27_utmeast != ''] and features/feature/location[@utm27_utmnorth != '']">
      <xsl:text>\begin{figure}[htp!]
  \centering
  \includegraphics[height=0.9\textheight,width=\textwidth,keepaspectratio=true]{</xsl:text>
      <xsl:value-of select="$gis_output_dir"/>
      <xsl:value-of select="@file_prefix"/>
      <xsl:text>_gis_map.jpg}
</xsl:text>

      <xsl:apply-templates select="." mode="index">
        <xsl:with-param name="suffix">|(</xsl:with-param>
      </xsl:apply-templates>

      <xsl:text>\end{figure}

\begin{figure}[htp!]
  \centering
  \includegraphics[width=\textwidth,keepaspectratio=true]{../../gis_maps/legend.png}
\end{figure}

\begin{center} { \footnotesize \textit{There may be some FROs shown on the maps that are not labeled.}} \end{center}
\clearpage

</xsl:text>

      <xsl:variable name="aerial_map_name" select="/regions/aerial_map[@type=$bulletin_type]"/>

      <xsl:if test="$aerial_map_name != ''">
        <xsl:text>\vspace*{8ex}

\begin{figure}[htp!]
  \centering
  \includegraphics[height=0.9\textheight,width=\textwidth,keepaspectratio=true]{</xsl:text>
      <xsl:value-of select="$gis_output_dir"/>
      <xsl:value-of select="@file_prefix"/>
      <xsl:text>_gis_</xsl:text>
      <xsl:value-of select="$aerial_map_name"/>
      <xsl:text>_aerial_map.jpg</xsl:text>
      <xsl:text>}
</xsl:text>

      <xsl:apply-templates select="." mode="index">
        <xsl:with-param name="suffix">|)</xsl:with-param>
      </xsl:apply-templates>

      <xsl:text>\end{figure}

\begin{center} { \footnotesize \textit{Aerial imagery courtesy of the </xsl:text>
      <xsl:value-of select="/regions/aerial_maps/aerial_map[@name=$aerial_map_name]/@description"/>
      <xsl:text>.}} \end{center}
\clearpage

</xsl:text>
      </xsl:if>
    </xsl:if>

    <xsl:text>\twocolumn
\setlength\parskip{1ex plus 0in minus 0in}
</xsl:text>

    <xsl:if test="introduction != ''">
      <xsl:text>\section*{Introduction} { </xsl:text>
      <xsl:value-of select="introduction"/>
      <xsl:text> }

</xsl:text>
    </xsl:if>


    <xsl:for-each select="features/feature">
      <xsl:sort select="name"/>

      <xsl:apply-templates select="." mode="photos"/>
      <xsl:apply-templates select="." mode="header"/>
      <xsl:apply-templates select="." mode="body"/>
    </xsl:for-each>


    <xsl:apply-templates select="features/feature/photo[@show_in_pdf='1' and @type != 'lineplot' and not (@type = 'map' and @ref) and @show_at_end='1']">
      <xsl:sort select="@sort_order" data-type="number"/>
      <xsl:sort select="@type" order="descending"/>
    </xsl:apply-templates>

    <xsl:text>\onecolumn
</xsl:text>
  </xsl:for-each>


  <!-- ############################ -->
  <!-- Show the embedded appendixes -->
  <!-- ############################ -->

  <xsl:text>\appendix \def\chaptername{Appendix}
</xsl:text>

  <xsl:apply-templates select="chapters/chapter[@is_appendix='1']"/>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Feature header                                                    ** -->
<!-- *********************************************************************** -->

<xsl:template match="feature" mode="header">
  <xsl:text>\vspace{1ex}

\begin{tikzpicture}
\node [mybox] (box){
\begin{minipage}[b]{0.95\columnwidth}
\phantomsection
\label{feature</xsl:text>
  <xsl:value-of select="@internal_id"/>
  <xsl:text>}
\begin{centering}
{\Large \bfseries \uppercase{</xsl:text>
  <xsl:value-of select="name"/> 
  <xsl:text>} } \\*
</xsl:text>

  <xsl:if test="aliases">
    <xsl:text>{\large \bfseries (</xsl:text>
    <xsl:for-each select="aliases">
      <xsl:if test="position() > 1">
        <xsl:text>, </xsl:text>
      </xsl:if>

      <xsl:value-of select="."/>
    </xsl:for-each>
    <xsl:text>)} \\[2ex]
</xsl:text>
  </xsl:if>

  <xsl:text>\end{centering}
</xsl:text>

  <xsl:if test="length != '' and length > 0">
    <xsl:text>Length: </xsl:text>

    <xsl:if test="length_based_on = 'estimate'">
      <xsl:text>$\sim$</xsl:text>
    </xsl:if>

    <xsl:choose>
      <xsl:when test="length &lt; 5280">
        <xsl:value-of select="format-number(length, '###,###')"/>
        <xsl:text> ft</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="format-number(length div 5280, '###,###.#')"/>
        <xsl:text> mi</xsl:text>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:if test="depth != '' and depth > 0">
      <xsl:text> \hfill Depth: </xsl:text>

      <xsl:if test="length_based_on = 'estimate'">
        <xsl:text>$\sim$</xsl:text>
      </xsl:if>

      <xsl:value-of select="format-number(depth, '###,###')"/>
      <xsl:text> ft</xsl:text>
    </xsl:if>

  <xsl:text> \\*
</xsl:text>
  </xsl:if>

  <xsl:for-each select="location">
    <xsl:if test="position() > 1">
      <!-- Newline for multiple entrances -->
      <xsl:text> \\
</xsl:text>
    </xsl:if>

    <xsl:if test="@name != '' and @name != ../name">
      <xsl:text>\textit{\textbf{</xsl:text>
      <xsl:value-of select="@name"/>
      <xsl:text>}} \\*
</xsl:text>
    </xsl:if>

    <xsl:if test="@wgs84_lat">
      <xsl:text>NAD27 UTM: \hfill </xsl:text>
      <xsl:value-of select="@utmzone"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="round(@utm27_utmnorth)"/>
      <xsl:text>N </xsl:text>
      <xsl:value-of select="round(@utm27_utmeast)"/>
      <xsl:text>E \\*
</xsl:text>

      <xsl:text>WGS84 Lat/Lon: \hfill </xsl:text>

      <xsl:call-template name="convert_to_ddmmss">
        <xsl:with-param name="dec_degrees"><xsl:value-of select="@wgs84_lat"/></xsl:with-param>
      </xsl:call-template>

      <xsl:text> / </xsl:text>

      <xsl:call-template name="convert_to_ddmmss">
        <xsl:with-param name="dec_degrees"><xsl:value-of select="@wgs84_lon"/></xsl:with-param>
      </xsl:call-template>
      <xsl:text> \\*
</xsl:text>
    </xsl:if>

    <xsl:if test="@ele != ''">
      <xsl:text>Elevation: </xsl:text>
      <xsl:value-of select="format-number(@ele, '###,###')"/>
      <xsl:text>&apos;</xsl:text>
    </xsl:if>

    <xsl:text> \hfill </xsl:text>
    <xsl:value-of select="@quad"/>
    <xsl:text> Quad \\*
</xsl:text>

    <xsl:choose>
      <xsl:when test="@coord_acquision='GPS'">
        <xsl:text>\textit{Coordinates acquired using a GPS receiver.} \\*
</xsl:text>
      </xsl:when>
      <xsl:when test="@coord_acquision='Other Topo Map'">
        <xsl:text>\textit{Coordinates acquired off of a topo map.} \\*
</xsl:text>
      </xsl:when>
      <xsl:when test="@coord_acquision='7.5 Topo Map'">
        <xsl:text>\textit{Coordinates acquired off of a 7.5' topo map.} \\*
</xsl:text>
      </xsl:when>
      <xsl:when test="@coord_acquision='Google Earth'">
        <xsl:text>\textit{Coordinates acquired using Google Earth.} \\*
</xsl:text>
      </xsl:when>
      <xsl:when test="@coord_acquision='Estimate'">
        <xsl:text>\textit{Coordinates are an estimate.} \\*
</xsl:text>
      </xsl:when>
      <xsl:when test="@coord_acquision='Filled In'">
        <xsl:text>\textit{Entrance is filled in; coordinates are an estimate.} \\*
</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>\textit{Coordinates acquired off of a topo map.} \\*
</xsl:text>
      </xsl:otherwise>
    </xsl:choose>

  </xsl:for-each>

  <xsl:if test="count(location) = 0">
        <xsl:text>\textit{Coordinates are not available.} \\*
</xsl:text>
  </xsl:if>

  <xsl:text>\vspace{-2ex}
\end{minipage}
};
\index{</xsl:text>
<xsl:value-of select="name"/>
<xsl:text>|(}
\end{tikzpicture}
\nopagebreak[4]
</xsl:text>

</xsl:template>


<!-- *********************************************************************** -->
<!-- ** References                                                        ** -->
<!-- *********************************************************************** -->

<xsl:template name="show_references">
  <xsl:if test="reference">
    <xsl:variable name="num_refs" select="count(reference)"/>

    <xsl:text>{ \footnotesize
\leftskip 0.2in
\parindent -0.1in
</xsl:text>

    <xsl:for-each select="reference">
      <xsl:sort select="@parsed_date"/>
      <xsl:sort select="@volume" data-type="number"/>
      <xsl:sort select="@number" data-type="number"/>
      <xsl:sort select="@pages" data-type="number"/>
      <xsl:sort select="@book"/>
      <xsl:sort select="@title"/>

      <xsl:if test="position() &lt; 3 or position() mod 2 = 0 or position() = $num_refs">
        <xsl:text>\nopagebreak[4]
</xsl:text>
      </xsl:if>

      <xsl:if test="position() > 1">
        <xsl:text>\vspace{-3.5ex}
</xsl:text>
      </xsl:if>

      <xsl:apply-templates select="."/>
    </xsl:for-each>

    <xsl:text>}
</xsl:text>
  </xsl:if>

  <xsl:text>

</xsl:text>
</xsl:template>


<xsl:template match="reference">
  <xsl:text>\textit{</xsl:text>

  <xsl:if test="@author != ''">
    <xsl:value-of select="@author"/>
  </xsl:if>

  <xsl:if test="@title != ''">
    <xsl:if test="@author != ''">
      <xsl:text>, </xsl:text>
    </xsl:if>

    <xsl:value-of select="@title"/>
  </xsl:if>

  <xsl:if test="@book != ''">
    <xsl:choose>
      <xsl:when test="@title != ''">
        <xsl:text>. </xsl:text>
      </xsl:when>
      <xsl:when test="@author != ''">
        <xsl:text>, </xsl:text>
      </xsl:when>
    </xsl:choose>

    <xsl:text>\textnormal{``</xsl:text>
    <xsl:value-of select="@book"/>
    <xsl:text>''}</xsl:text>
  </xsl:if>

  <xsl:if test="@volume != ''">
    <xsl:text>, V</xsl:text>
    <xsl:value-of select="@volume"/>

    <xsl:if test="@number != ''">
      <xsl:text>n</xsl:text>
      <xsl:value-of select="@number"/>
    </xsl:if>

    <xsl:if test="@pages != ''">
      <xsl:choose>
        <xsl:when test="contains(@pages, '-') or contains(@pages, ',')">
          <xsl:text>pp</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>p</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:value-of select="@pages"/>
    </xsl:if>
  </xsl:if>

  <xsl:if test="@url != ''">
    <xsl:text>, URL: </xsl:text>
    <xsl:value-of select="@url"/>
  </xsl:if>

  <xsl:if test="@extra != ''">
    <xsl:text>, </xsl:text>
    <xsl:value-of select="@extra"/>
  </xsl:if>

  <xsl:text>, </xsl:text>
  <xsl:choose>
    <xsl:when test="@date != ''">
      <xsl:value-of select="@date"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text>date unknown</xsl:text>
    </xsl:otherwise>
  </xsl:choose>

  <xsl:if test="@volume = '' and @pages != ''">
    <xsl:choose>
      <xsl:when test="contains(@pages, '-') or contains(@pages, ',')">
        <xsl:text>, Pages </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>, Page </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:value-of select="@pages"/>
  </xsl:if>

  <xsl:text>} \\

</xsl:text>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Feature body                                                      ** -->
<!-- *********************************************************************** -->

<xsl:template match="quote">
  <xsl:text>\textit{</xsl:text>
  <xsl:value-of select="."/>
  <xsl:text>}</xsl:text>
</xsl:template>


<xsl:template match="feature" mode="body">
  <xsl:if test="hazards">
    <xsl:text>
{ \bf </xsl:text>
    <xsl:value-of select="hazards"/>
    <xsl:text> }

</xsl:text>
  </xsl:if>

  <xsl:choose>
    <xsl:when test="desc">
      <xsl:for-each select="desc/para">
        <xsl:if test="position() > 1">
          <xsl:text>

</xsl:text>
        </xsl:if>

        <xsl:apply-templates/>
      </xsl:for-each>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text>There is currently no description available.</xsl:text>
    </xsl:otherwise>
  </xsl:choose>

  <xsl:if test="geology">
    <xsl:text>

</xsl:text>
    <xsl:value-of select="geology"/>
  </xsl:if>

  <xsl:if test="biology">
    <xsl:text>

{ \bf Biology:} </xsl:text>
    <xsl:value-of select="biology"/>
  </xsl:if>

  <xsl:if test="history">
    <xsl:text>

{ \bf History:} </xsl:text>
    <xsl:value-of select="history"/>
  </xsl:if>

  <xsl:if test="desc/@author">
    <xsl:text> \textit{(</xsl:text>
    <xsl:value-of select="desc/@author"/>
    <xsl:text>)}</xsl:text>
  </xsl:if>

  <xsl:text>

</xsl:text>

  <xsl:call-template name="show_references"/>

  <xsl:text>\index{</xsl:text>
  <xsl:value-of select="name"/>
  <xsl:text>|)}
</xsl:text>

</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Feature photos                                                    ** -->
<!-- *********************************************************************** -->

<xsl:template match="feature/photo" mode="filename">
  <xsl:value-of select="@base_directory"/>
  <xsl:text>/</xsl:text>

  <xsl:choose>
    <xsl:when test="$feature_photo='primary'">
      <xsl:value-of select="@primary_filename"/>
    </xsl:when>
    <xsl:when test="@secondary_filename != ''">
      <xsl:value-of select="@secondary_filename"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="@primary_filename"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template match="feature/photo">
  <xsl:if test="@num_in_pdf mod 48 = 0">
    <xsl:text>\clearpage
</xsl:text>
  </xsl:if>

  <xsl:variable name="figure_opts">
    <xsl:if test="@scale != 'column'">
      <xsl:text>*</xsl:text>
    </xsl:if>
  </xsl:variable>

  <xsl:variable name="graphic_opts">
    <xsl:text>keepaspectratio</xsl:text>
    <xsl:if test="@rotate">
      <xsl:text>,angle=</xsl:text>
      <xsl:value-of select="@rotate"/>
    </xsl:if>

    <xsl:choose>
      <xsl:when test="@scale='fullpage' and @caption">
        <xsl:text>,height=0.9\textheight,width=\textwidth</xsl:text>
      </xsl:when>
      <xsl:when test="@scale='fullpage'">
        <xsl:text>,height=\textheight,width=\textwidth</xsl:text>
      </xsl:when>
      <xsl:when test="@scale='halfpage'">
        <xsl:text>,height=0.4\textheight,width=\textwidth</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>,height=.4\textheight,width=\columnwidth</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:text>\begin{figure</xsl:text>
  <xsl:value-of select="$figure_opts"/>
  <xsl:text>}[tp]
\phantomsection
\index{</xsl:text>
  <xsl:value-of select="../name"/>
  <xsl:text>}</xsl:text>

  <xsl:for-each select="index">
    <xsl:text>\index{</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>}</xsl:text>
  </xsl:for-each>

  <xsl:text>
\centering
</xsl:text>

  <xsl:text>  \includegraphics[</xsl:text>
  <xsl:value-of select="$graphic_opts"/>
  <xsl:text>]{</xsl:text>
  <xsl:apply-templates select="." mode="filename"/>
  <xsl:text>}
</xsl:text>

  <xsl:if test="@caption">
    <xsl:text> \caption{</xsl:text>
    <xsl:value-of select="@caption"/>
    <xsl:text>}
</xsl:text>
  </xsl:if>

  <xsl:text>  \label{</xsl:text>
  <xsl:value-of select="@id"/>
  <xsl:text>}
\end{figure</xsl:text>
  <xsl:value-of select="$figure_opts"/>
  <xsl:text>}
</xsl:text>

  <xsl:text>

</xsl:text>
</xsl:template>


<xsl:template match="feature" mode="photos">
  <xsl:apply-templates select="photo[@show_in_pdf='1' and @type != 'lineplot' and not (@type = 'map' and @ref) and @show_at_end='0']">
    <xsl:sort select="@sort_order" data-type="number"/>
    <xsl:sort select="@type" order="descending"/>
  </xsl:apply-templates>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Bibliography                                                      ** -->
<!-- *********************************************************************** -->

<xsl:template match="/regions" mode="bibliography">
  <xsl:text>\chapter{Bibliography}
\begin{multicols}{2}
{ 
\setlength{\parskip}{-2ex plus 0in minus 0in}
\parindent -0.1in
\leftskip 0.2in
\it
\footnotesize
</xsl:text>

  <xsl:for-each select="/regions/all_references/reference[@hidden_in_bibliography='False' and generate-id() = generate-id(key('distinctRefs', concat(@author, @title, @book, @volume, @number, @pages, @url, @date, @extra)))]">
      <xsl:sort select="@author"/>
      <xsl:sort select="@parsed_date"/>
      <xsl:sort select="@volume" data-type="number"/>
      <xsl:sort select="@number" data-type="number"/>
      <xsl:sort select="@pages" data-type="number"/>
      <xsl:sort select="@book"/>
      <xsl:sort select="@title"/>

      <xsl:apply-templates select="."/>
  </xsl:for-each>

  <xsl:text>
}
\end{multicols}
</xsl:text>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Document index                                                    ** -->
<!-- *********************************************************************** -->

<xsl:template match="/regions" mode="photos_index">
  <xsl:text>\chapter{List of Photos}
\begin{center}
\begin{longtable}{|c|c|c|c|}
    %This is the header for the first page of the table...
    \hline
    \rowcolor[rgb]{0.9,0.9,0.9} \centering Page &amp; Cave &amp; People Shown In Photo &amp; Photographer \\
    \hline
  \endfirsthead

    %This is the header for the remaining page(s) of the table...
    \hline
    \rowcolor[rgb]{0.9,0.9,0.9} \centering Page &amp; Cave &amp; People Shown In Photo &amp; Photographer \\
    \hline
  \endhead

    %This is the footer for all pages except the last page of the table...
    \hline
  \endfoot

    %This is the footer for the last page of the table...
    \hline 
  \endlastfoot
</xsl:text>

  <xsl:if test="/regions/photo_index_header != ''">
    <xsl:value-of select="/regions/photo_index_header"/>
    <xsl:text>
</xsl:text>
  </xsl:if>

  <xsl:for-each select="region">
    <xsl:sort select="@name"/>

    <xsl:for-each select="features/feature/photo[@show_in_pdf='1' and @id != '' and @type != 'map']">
      <xsl:sort select="@show_at_end" data-type="number"/>
      <xsl:sort select="../name"/>
      <xsl:sort select="@sort_order" data-type="number"/>
      <xsl:sort select="@type" order="descending"/>

      <xsl:if test="position() mod 2 = 0">
        <xsl:text>\rowcolor[rgb]{0.95,0.95,0.95} </xsl:text>
      </xsl:if>
  
      <xsl:text>\pageref{</xsl:text>
      <xsl:value-of select="@id"/>
      <xsl:text>} </xsl:text>
      <xsl:text> &amp; </xsl:text>
      <xsl:value-of select="../name"/>
      <xsl:text> &amp; </xsl:text>
      <xsl:value-of select="@people_shown"/>
      <xsl:text> &amp; </xsl:text>
      <xsl:value-of select="@author"/>
      <xsl:text> \\
  </xsl:text>
    </xsl:for-each>
  </xsl:for-each>

  <xsl:text>\end{longtable}
\end{center}
</xsl:text>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Document index                                                    ** -->
<!-- *********************************************************************** -->

<xsl:template match="feature" mode="object_page_num">
  <xsl:param name="type"/>

  <xsl:if test="photo[@show_in_pdf='1' and @type=$type]">
    <xsl:text>\pageref{</xsl:text>

    <xsl:choose>
      <xsl:when test="photo[@show_in_pdf='1' and @type=$type]/@id">
        <xsl:value-of select="photo[@show_in_pdf='1' and @type=$type]/@id"/>
      </xsl:when>
      <xsl:when test="photo[@show_in_pdf='1' and @type=$type]/@ref">
        <xsl:value-of select="photo[@show_in_pdf='1' and @type=$type]/@ref"/>
      </xsl:when>
      <xsl:otherwise>
         <xsl:text>UNKNOWN</xsl:text>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:text>}</xsl:text>
  </xsl:if>
</xsl:template>


<xsl:template match="feature" mode="caves_index">
  <xsl:text> &amp; </xsl:text>

  <xsl:value-of select="@id"/>
  <xsl:text> &amp; </xsl:text>

  <xsl:value-of select="@type"/>
  <xsl:text> &amp; </xsl:text>


  <xsl:if test="length and length > 0">
    <xsl:value-of select="format-number(length, '###,###')"/>
    <xsl:text>$^\prime$</xsl:text>
  </xsl:if>
  <xsl:text> &amp; </xsl:text>

  <xsl:if test="depth and depth > 0">
    <xsl:value-of select="format-number(depth, '###,###')"/>
    <xsl:text>$^\prime$</xsl:text>
  </xsl:if>
  <xsl:text> &amp; </xsl:text>

  <xsl:text>\pageref{feature</xsl:text>
  <xsl:value-of select="@internal_id"/>
  <xsl:text>}</xsl:text>
  <xsl:text> &amp; </xsl:text>

  <xsl:apply-templates select="." mode="object_page_num">
    <xsl:with-param name="type">map</xsl:with-param>
  </xsl:apply-templates>
  <xsl:text> &amp; </xsl:text>

  <xsl:apply-templates select="." mode="object_page_num">
    <xsl:with-param name="type">entrance_picture</xsl:with-param>
  </xsl:apply-templates>

  <xsl:text> \\
</xsl:text>
</xsl:template>


<xsl:template match="feature" mode="alias_index_with_pagenums">
  <xsl:value-of select="@id"/>
  <xsl:text> &amp; </xsl:text>

  <xsl:value-of select="@type"/>
  <xsl:text> &amp; </xsl:text>

  <xsl:text> - &amp; </xsl:text>

  <xsl:text> - &amp; </xsl:text>

  <xsl:text>\pageref{feature</xsl:text>
  <xsl:value-of select="@internal_id"/>
  <xsl:text>}</xsl:text>
  <xsl:text> &amp; </xsl:text>

  <xsl:apply-templates select="." mode="object_page_num">
    <xsl:with-param name="type">map</xsl:with-param>
  </xsl:apply-templates>
  <xsl:text> &amp; </xsl:text>

  <xsl:apply-templates select="." mode="object_page_num">
    <xsl:with-param name="type">entrance_picture</xsl:with-param>
  </xsl:apply-templates>

  <xsl:text> \\
</xsl:text>
</xsl:template>


<xsl:template match="index" mode="alias_index_without_pagenums">
  <xsl:text> - &amp; </xsl:text>
  <xsl:text> - &amp; </xsl:text>
  <xsl:text> - &amp; </xsl:text>
  <xsl:text> - &amp; </xsl:text>
  <xsl:text> - &amp; </xsl:text>
  <xsl:text> - &amp; </xsl:text>
  <xsl:text> - \\
</xsl:text>
</xsl:template>


<xsl:template match="/regions" mode="caves_index">
  <xsl:text>\chapter{Index of Caves}
\begin{center}
\begin{longtable}{| p{5.5cm} |c|c|c|c|c|c|c|}
    %This is the header for the first page of the table...
    \hline
    \rowcolor[rgb]{0.9,0.9,0.9} \centering Name &amp; ID &amp; Type &amp; Length &amp; Depth &amp; Page &amp; Map &amp; Ent. \\
    \rowcolor[rgb]{0.9,0.9,0.9} &amp; &amp; &amp; &amp; &amp; &amp; &amp; Photo \\
    \hline
  \endfirsthead

    %This is the header for the remaining page(s) of the table...
    \hline
    \rowcolor[rgb]{0.9,0.9,0.9} \centering Name &amp; ID &amp; Type &amp; Length &amp; Depth &amp; Page &amp; Map &amp; Ent. \\
    \rowcolor[rgb]{0.9,0.9,0.9} &amp; &amp; &amp; &amp; &amp; &amp; &amp; Photo \\
    \hline
  \endhead

    %This is the footer for all pages except the last page of the table...
    \hline
  \endfoot

    %This is the footer for the last page of the table...
    \hline
  \endlastfoot
</xsl:text>

  <xsl:for-each select="feature_indexes/index">
    <xsl:sort select="@name"/>

    <xsl:variable name="feat_name" select="@name"/>
    <xsl:variable name="pos" select="position()"/>

    <xsl:if test="position() mod 2 = 0">
      <xsl:text>\rowcolor[rgb]{0.95,0.95,0.95} </xsl:text>
    </xsl:if>

    <xsl:value-of select="@name"/>

    <xsl:choose>
      <xsl:when test="@is_primary='1'">
        <xsl:apply-templates select="/regions/region/features/feature[name=$feat_name]" mode="caves_index"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>\begin{description}
\setlength{\parskip}{-2ex plus 0in minus 0in}
\item \textit{see </xsl:text>
        <xsl:variable name="num_features"><xsl:value-of select="count(feature_id)"/></xsl:variable>
        <xsl:for-each select="feature_id">
          <xsl:choose>
            <xsl:when test="position() > 1 and position() = $num_features">
              <xsl:text> and </xsl:text>
            </xsl:when>
            <xsl:when test="position() > 1">
              <xsl:text>, </xsl:text>
            </xsl:when>
          </xsl:choose>

          <xsl:variable name="feature_id"><xsl:value-of select="."/></xsl:variable>
          <xsl:value-of select="/regions/region/features/feature[@internal_id=$feature_id]/name"/>
        </xsl:for-each>
        <xsl:text>\vspace{-2ex} } \end{description} &amp; </xsl:text>

        <xsl:choose>
          <xsl:when test="$num_features > 1">
            <xsl:apply-templates select="." mode="alias_index_without_pagenums"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="feature_id"><xsl:value-of select="feature_id[1]"/></xsl:variable>
            <xsl:apply-templates select="/regions/region/features/feature[@internal_id=$feature_id]" mode="alias_index_with_pagenums"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:for-each>

  <xsl:text>\end{longtable}
\end{center}
</xsl:text>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Document footer                                                   ** -->
<!-- *********************************************************************** -->

<xsl:template name="show_document_footer">
  <xsl:if test="back_cover/@image">
    <xsl:text>% ---- Back Cover ----
\showcoverimage{</xsl:text>

    <xsl:value-of select="back_cover/@image"/>

    <xsl:text>}
</xsl:text>
  </xsl:if>

<xsl:text>\end{document}
</xsl:text>
</xsl:template>

</xsl:stylesheet>

