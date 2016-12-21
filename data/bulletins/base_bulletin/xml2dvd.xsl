<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:exsl="http://exslt.org/common" version="1.0">
  <xsl:output method="text" indent="no" encoding="US-ASCII"/>
  <xsl:strip-space elements="*"/>

  <xsl:variable name="base_dir">output/dvd</xsl:variable>
  <xsl:variable name="map_dir"><xsl:value-of select="$base_dir"/>/Maps/</xsl:variable>
  <xsl:variable name="refs_dir"><xsl:value-of select="$base_dir"/>/References/</xsl:variable>
  <xsl:variable name="entrance_photos_dir"><xsl:value-of select="$base_dir"/>/Entrance Photos/</xsl:variable>
  <xsl:variable name="in_cave_photos_dir"><xsl:value-of select="$base_dir"/>/In Cave Photos/</xsl:variable>
  <xsl:variable name="surface_photos_dir"><xsl:value-of select="$base_dir"/>/Surface Photos/</xsl:variable>

  <xsl:template match="/regions">
    <xsl:text>rm -rf </xsl:text>
    <xsl:value-of select="$base_dir"/>
    <xsl:text>
mkdir -p </xsl:text>
    <xsl:value-of select="$base_dir"/>
    <xsl:text>
</xsl:text>


   <xsl:variable name="readme"><xsl:value-of select="$base_dir"/>/README.txt</xsl:variable>
   <xsl:text>cat &lt;&lt; __EOF__ &gt; </xsl:text>
   <xsl:value-of select="$readme"/>
   <xsl:text>
</xsl:text>
   <xsl:value-of select="dvd_readme"/>
   <xsl:text>
__EOF__
</xsl:text>

   <!--
   <xsl:variable name="autorun"><xsl:value-of select="$base_dir"/>/autorun.inf</xsl:variable>
   <xsl:text>cat &lt;&lt; __EOF__ &gt; </xsl:text>
   <xsl:value-of select="$autorun"/>
   <xsl:text>
[autorun]
open=start README.txt
__EOF__
</xsl:text>
   -->


    <xsl:apply-templates select="." mode="feature_photos">
      <xsl:with-param name="type">map</xsl:with-param>
      <xsl:with-param name="descr">Map</xsl:with-param>
      <xsl:with-param name="dest_dir"><xsl:value-of select="$map_dir"/></xsl:with-param>
    </xsl:apply-templates>

    <xsl:apply-templates select="." mode="feature_photos">
      <xsl:with-param name="type">entrance_picture</xsl:with-param>
      <xsl:with-param name="descr">Entrance Photo</xsl:with-param>
      <xsl:with-param name="dest_dir"><xsl:value-of select="$entrance_photos_dir"/></xsl:with-param>
    </xsl:apply-templates>

    <xsl:apply-templates select="." mode="feature_photos">
      <xsl:with-param name="type">in_cave_picture</xsl:with-param>
      <xsl:with-param name="descr">In Cave Photo</xsl:with-param>
      <xsl:with-param name="dest_dir"><xsl:value-of select="$in_cave_photos_dir"/></xsl:with-param>
    </xsl:apply-templates>

    <xsl:apply-templates select="." mode="feature_photos">
      <xsl:with-param name="type">surface_picture</xsl:with-param>
      <xsl:with-param name="descr">Surface Photo</xsl:with-param>
      <xsl:with-param name="dest_dir"><xsl:value-of select="$surface_photos_dir"/></xsl:with-param>
    </xsl:apply-templates>

    <xsl:text>zip -r </xsl:text>
    <xsl:value-of select="$base_dir"/>
    <xsl:text>/dvd.zip </xsl:text>
    <xsl:value-of select="$base_dir"/>
    <xsl:text>
</xsl:text>
  </xsl:template>


  <xsl:template match="/regions" mode="feature_photos">
    <xsl:param name="type"/>
    <xsl:param name="descr"/>
    <xsl:param name="dest_dir"/>

    <xsl:text>mkdir -p "</xsl:text>
    <xsl:value-of select="$dest_dir"/>
    <xsl:text>"
</xsl:text>

    <xsl:for-each select="region/features/feature">
      <xsl:variable name="total" select="count(photo[@include_on_dvd='1' and @type=$type and @primary_filename != ''])"/>
      <xsl:for-each select="photo[@include_on_dvd='1' and @type=$type and @primary_filename != '']">
        <xsl:sort select="@sort_order" data-type="number"/>

        <xsl:text>ln "</xsl:text>
        <xsl:value-of select="@base_directory"/>
        <xsl:value-of select="@primary_filename"/>
        <xsl:text>" "</xsl:text>
        <xsl:value-of select="$dest_dir"/>
        <xsl:value-of select="../name"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="$descr"/>

        <xsl:if test="$total > 1">
          <xsl:text> - </xsl:text>
          <xsl:value-of select="format-number(position(), '00')"/>
          <xsl:text> of </xsl:text>
          <xsl:value-of select="format-number($total, '00')"/>
        </xsl:if>

        <xsl:if test="@author != ''">
          <xsl:text> - </xsl:text>
          <xsl:value-of select="@author"/>
        </xsl:if>

        <xsl:value-of select="translate(substring(@primary_filename, string-length(@primary_filename) - 3),'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"/>
        <xsl:text>"
</xsl:text>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
