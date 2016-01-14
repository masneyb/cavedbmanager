<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY nbsp "&#160;">
<!ENTITY quot "&#34;">
<!ENTITY deg  "&#176;">
]>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="text" indent="no" encoding="US-ASCII"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/regions">
    <xsl:call-template name="show_title_page"/>
    <xsl:call-template name="show_preamble_page"/>
    <xsl:call-template name="show_contributor_page"/>
    <xsl:call-template name="show_document_body"/>
  </xsl:template>

<!-- *********************************************************************** -->
<!-- ** Preamble and title pages                                          ** -->
<!-- *********************************************************************** -->

<xsl:template name="show_title_page">
  <xsl:value-of select="/regions/title_page"/>
  <xsl:text>

</xsl:text>
</xsl:template>

<xsl:template name="show_preamble_page">
  <xsl:value-of select="/regions/preamble_page"/>
  <xsl:text>

</xsl:text>
</xsl:template>

<xsl:template name="show_contributor_page">
  <xsl:value-of select="/regions/contributor_page"/>
  <xsl:text>

</xsl:text>
</xsl:template>

<!-- *********************************************************************** -->
<!-- ** Document body                                                     ** -->
<!-- *********************************************************************** -->

<xsl:template match="/regions/chapters/chapter">
  <xsl:value-of select="@title"/>
  <xsl:text>
</xsl:text>

  <xsl:for-each select="section">
    <xsl:if test="@title">
      <xsl:value-of select="@title"/>
      <xsl:text>
</xsl:text>
    </xsl:if>

    <xsl:if test="@subtitle">
      <xsl:value-of select="@subtitle"/>
      <xsl:text>
</xsl:text>
    </xsl:if>

    <xsl:value-of select="."/>
    <xsl:text>
</xsl:text>
  </xsl:for-each>
</xsl:template>


<xsl:template name="show_document_body">
  <xsl:apply-templates select="chapters/chapter[@is_appendix='0']"/>

  <xsl:text>Introduction
</xsl:text>

  <xsl:if test="caves_header != ''">
    <xsl:value-of select="caves_header"/>
    <xsl:text>
</xsl:text>
  </xsl:if>

  <xsl:for-each select="region">
    <xsl:value-of select="@name"/>
    <xsl:text>
</xsl:text>

    <xsl:if test="introduction != ''">
      <xsl:value-of select="introduction"/>
      <xsl:text>
</xsl:text>
    </xsl:if>


    <xsl:for-each select="features/feature">
      <xsl:sort select="name"/>

      <xsl:apply-templates select="." mode="header"/>
      <xsl:apply-templates select="." mode="body"/>
      <xsl:text>

</xsl:text>
    </xsl:for-each>
  </xsl:for-each>


  <!-- ############################ -->
  <!-- Show the embedded appendixes -->
  <!-- ############################ -->

  <xsl:apply-templates select="chapters/chapter[@is_appendix='1']"/>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Feature header                                                    ** -->
<!-- *********************************************************************** -->

<xsl:template match="feature" mode="header">
  <xsl:value-of select="name"/> 
  <xsl:text>
</xsl:text>

  <xsl:for-each select="aliases">
    <xsl:value-of select="."/>
    <xsl:text>
</xsl:text>
  </xsl:for-each>

  <xsl:for-each select="location">
    <xsl:if test="@name != '' and @name != ../name">
      <xsl:value-of select="@name"/>
      <xsl:text>
</xsl:text>
    </xsl:if>
  </xsl:for-each>

  <xsl:text>
</xsl:text>
</xsl:template>


<!-- *********************************************************************** -->
<!-- ** Feature body                                                      ** -->
<!-- *********************************************************************** -->

<xsl:template match="feature" mode="body">
  <xsl:if test="hazards">
    <xsl:value-of select="hazards"/>
    <xsl:text>
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
    <xsl:value-of select="geology"/>
    <xsl:text>
</xsl:text>
  </xsl:if>

  <xsl:if test="biology">
    <xsl:value-of select="biology"/>
    <xsl:text>
</xsl:text>
  </xsl:if>

  <xsl:if test="history">
    <xsl:value-of select="history"/>
    <xsl:text>
</xsl:text>
  </xsl:if>

  <xsl:if test="desc/@author">
    <xsl:text> (</xsl:text>
    <xsl:value-of select="desc/@author"/>
    <xsl:text>)</xsl:text>
  </xsl:if>

  <xsl:text>
</xsl:text>

  <xsl:if test="reference">
    <xsl:variable name="num_refs" select="count(reference)"/>

    <xsl:for-each select="reference">
      <xsl:sort select="@parsed_date"/>
      <xsl:sort select="@volume" data-type="number"/>
      <xsl:sort select="@number" data-type="number"/>
      <xsl:sort select="@book"/>
      <xsl:sort select="@title"/>

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
            <xsl:text>: </xsl:text>
          </xsl:when>
          <xsl:when test="@author != ''">
            <xsl:text>, </xsl:text>
          </xsl:when>
        </xsl:choose>

        <xsl:value-of select="@book"/>
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

      <xsl:text>
</xsl:text>
    </xsl:for-each>
  </xsl:if>

  <xsl:text>
</xsl:text>

</xsl:template>

</xsl:stylesheet>

