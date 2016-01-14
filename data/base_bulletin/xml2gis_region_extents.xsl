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


<xsl:template match="/regions">
  <xsl:apply-templates select="." mode="start">
    <xsl:with-param name="gis_xBuffer"><xsl:value-of select="$gis_xBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_yBuffer"><xsl:value-of select="$gis_yBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_bottom_buffer"><xsl:value-of select="$gis_bottom_buffer"/></xsl:with-param>
  </xsl:apply-templates>
</xsl:template>


<xsl:template match="/regions" mode="header">
  <xsl:text>region_name,wkt
</xsl:text>
</xsl:template>


<xsl:template match="/regions/region" mode="display_region_map">
  <xsl:param name="minx"/>
  <xsl:param name="miny"/>
  <xsl:param name="maxx"/>
  <xsl:param name="maxy"/>

  <xsl:if test="@show_gis_map = '1'">
    <xsl:text>"</xsl:text>
    <xsl:value-of select="@map_name"/>
    <xsl:text>",</xsl:text>

    <xsl:text>"POLYGON((</xsl:text>

    <xsl:value-of select="$minx"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="$miny"/>
    <xsl:text>, </xsl:text>

    <xsl:value-of select="$maxx"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="$miny"/>
    <xsl:text>, </xsl:text>

    <xsl:value-of select="$maxx"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="$maxy"/>
    <xsl:text>, </xsl:text>

    <xsl:value-of select="$minx"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="$maxy"/>
    <xsl:text>, </xsl:text>

    <xsl:value-of select="$minx"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="$miny"/>
    <xsl:text>))"</xsl:text>

    <xsl:text>
</xsl:text>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>
