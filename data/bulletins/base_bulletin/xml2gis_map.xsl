<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="text" indent="no" encoding="US-ASCII"/>

<xsl:include href="gis_common.xsl"/>

<xsl:param name="gis_bin"/>
<xsl:param name="gis_project"/>
<xsl:param name="gis_output_dir"/>
<xsl:param name="gis_file_suffix"/>
<xsl:param name="gis_xBuffer"/>
<xsl:param name="gis_yBuffer"/>
<xsl:param name="gis_bottom_buffer"/>

<xsl:template name="generate_gis_map">
  <xsl:param name="file_prefix"/>
  <xsl:param name="extent"/>
  <xsl:param name="opts"/>
  <xsl:param name="expected_hashcode"/>

  <xsl:variable name="hashcode_filename">
    <xsl:text>output/gis_maps/</xsl:text>
    <xsl:value-of select="$file_prefix"/>
    <xsl:value-of select="$gis_file_suffix"/>
    <xsl:text>.hashcode</xsl:text>
  </xsl:variable>
    
  <xsl:text>if [ ! -f </xsl:text>
  <xsl:value-of select="$hashcode_filename"/>
  <xsl:text> ] || [ $(cat </xsl:text>
  <xsl:value-of select="$hashcode_filename"/>
  <xsl:text>) != "</xsl:text>
  <xsl:value-of select="$expected_hashcode"/>
  <xsl:text>" ] ; then
  </xsl:text> 

  <xsl:value-of select="$gis_bin"/>

  <xsl:text> -m </xsl:text>
  <xsl:value-of select="$gis_project"/>

  <xsl:text> -o </xsl:text>
  <xsl:value-of select="$file_prefix"/>
  <xsl:value-of select="$gis_file_suffix"/>

  <xsl:if test="$opts != ''">
    <xsl:text> </xsl:text>
    <xsl:value-of select="$opts"/>
    <xsl:text> </xsl:text>
  </xsl:if>

  <xsl:text> -e </xsl:text>

  <xsl:value-of select="$extent"/>
  <xsl:text>
  if [ "$?" = "0" ] ; then
    echo "</xsl:text>
  <xsl:value-of select="$expected_hashcode"/>
  <xsl:text>" > </xsl:text>
  <xsl:value-of select="$hashcode_filename"/>
  <xsl:text>
  fi
fi
</xsl:text>
</xsl:template>


<xsl:template match="/regions">
  <xsl:apply-templates select="." mode="start">
    <xsl:with-param name="gis_xBuffer"><xsl:value-of select="$gis_xBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_yBuffer"><xsl:value-of select="$gis_yBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_bottom_buffer"><xsl:value-of select="$gis_bottom_buffer"/></xsl:with-param>
  </xsl:apply-templates>
</xsl:template>


<xsl:template match="/regions" mode="display_regionwide_map">
  <xsl:param name="minx"/>
  <xsl:param name="miny"/>
  <xsl:param name="maxx"/>
  <xsl:param name="maxy"/>

  <xsl:call-template name="generate_gis_map">
    <xsl:with-param name="file_prefix"><xsl:value-of select="@file_prefix"/></xsl:with-param>
    <xsl:with-param name="extent">
      <xsl:value-of select="$minx"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$miny"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$maxx"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$maxy"/>
    </xsl:with-param>
    <xsl:with-param name="expected_hashcode"><xsl:value-of select="@all_regions_gis_hash"/></xsl:with-param>
  </xsl:call-template>
</xsl:template>


<xsl:template match="/regions/region" mode="display_region_map">
  <xsl:param name="minx"/>
  <xsl:param name="miny"/>
  <xsl:param name="maxx"/>
  <xsl:param name="maxy"/>

  <xsl:call-template name="generate_gis_map">
    <xsl:with-param name="file_prefix"><xsl:value-of select="@file_prefix"/></xsl:with-param>
    <xsl:with-param name="extent">
      <xsl:value-of select="$minx"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$miny"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$maxx"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$maxy"/>
    </xsl:with-param>
    <xsl:with-param name="expected_hashcode"><xsl:value-of select="@gis_hash"/></xsl:with-param>
  </xsl:call-template>
</xsl:template>

</xsl:stylesheet>
