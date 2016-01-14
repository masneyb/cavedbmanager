<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="text" indent="no" encoding="US-ASCII"/>

<xsl:template match="/regions" mode="start">
  <xsl:param name="gis_xBuffer"/>
  <xsl:param name="gis_yBuffer"/>
  <xsl:param name="gis_bottom_buffer"/>

  <xsl:apply-templates select="." mode="header"/>

  <xsl:apply-templates select="." mode="calculate_regionwide_map">
    <xsl:with-param name="gis_xBuffer"><xsl:value-of select="$gis_xBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_yBuffer"><xsl:value-of select="$gis_yBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_bottom_buffer"><xsl:value-of select="$gis_bottom_buffer"/></xsl:with-param>
  </xsl:apply-templates>

  <xsl:apply-templates select="." mode="calculate_region_maps">
    <xsl:with-param name="gis_xBuffer"><xsl:value-of select="$gis_xBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_yBuffer"><xsl:value-of select="$gis_yBuffer"/></xsl:with-param>
    <xsl:with-param name="gis_bottom_buffer"><xsl:value-of select="$gis_bottom_buffer"/></xsl:with-param>
  </xsl:apply-templates>
</xsl:template>


<xsl:template match="/regions" mode="header">
  <!-- Nothing. Overridden in other template files -->
</xsl:template>


<!-- *********************************** -->
<!-- Write out a GIS map for each region -->
<!-- *********************************** -->

<xsl:template match="/regions/region" mode="display_region_map">
  <xsl:param name="minx"/>
  <xsl:param name="miny"/>
  <xsl:param name="maxx"/>
  <xsl:param name="maxy"/>

  <!-- Nothing. Overridden in other template files -->
</xsl:template>


<xsl:template match="/regions" mode="calculate_region_maps">
  <xsl:param name="gis_xBuffer"/>
  <xsl:param name="gis_yBuffer"/>
  <xsl:param name="gis_bottom_buffer"/>

  <xsl:for-each select="region">
    <xsl:if test="features/feature/location[@wgs84_lon != ''] and features/feature/location[@wgs84_lat != '']">
      <xsl:variable name="minx">
        <xsl:for-each select="features/feature/location[@wgs84_lon != '']">
          <xsl:sort select="@wgs84_lon" data-type="number"/>
          <xsl:if test="position() = 1">
            <xsl:value-of select="@wgs84_lon - $gis_xBuffer"/>
	  </xsl:if>
        </xsl:for-each>
      </xsl:variable>

      <xsl:variable name="miny">
        <xsl:for-each select="features/feature/location[@wgs84_lat != '']">
          <xsl:sort select="@wgs84_lat" data-type="number"/>
          <xsl:if test="position() = 1">
            <xsl:value-of select="@wgs84_lat - $gis_yBuffer - $gis_bottom_buffer"/>
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>

      <xsl:variable name="maxx">
        <xsl:for-each select="features/feature/location[@wgs84_lon != '']">
          <xsl:sort select="@wgs84_lon" data-type="number" order="descending"/>
          <xsl:if test="position() = 1">
            <xsl:value-of select="@wgs84_lon + $gis_xBuffer"/>
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>

      <xsl:variable name="maxy">
        <xsl:for-each select="features/feature/location[@wgs84_lat != '']">
          <xsl:sort select="@wgs84_lat" data-type="number" order="descending"/>
          <xsl:if test="position() = 1">
	    <xsl:value-of select="@wgs84_lat + $gis_yBuffer"/>
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>

      <xsl:apply-templates select="." mode="display_region_map">
        <xsl:with-param name="minx"><xsl:value-of select="$minx"/></xsl:with-param>
        <xsl:with-param name="miny"><xsl:value-of select="$miny"/></xsl:with-param>
        <xsl:with-param name="maxx"><xsl:value-of select="$maxx"/></xsl:with-param>
        <xsl:with-param name="maxy"><xsl:value-of select="$maxy"/></xsl:with-param>
      </xsl:apply-templates>
    </xsl:if>
  </xsl:for-each>
</xsl:template>


<!-- *********************************** -->
<!-- Write out a GIS map for all regions -->
<!-- *********************************** -->

<xsl:template match="/regions" mode="display_regionwide_map">
  <xsl:param name="minx"/>
  <xsl:param name="miny"/>
  <xsl:param name="maxx"/>
  <xsl:param name="maxy"/>

  <!-- Nothing. Overridden in other template files -->
</xsl:template>


<xsl:template match="/regions" mode="calculate_regionwide_map">
  <xsl:param name="gis_xBuffer"/>
  <xsl:param name="gis_yBuffer"/>
  <xsl:param name="gis_bottom_buffer"/>

  <xsl:variable name="minx">
    <xsl:for-each select="region/features/feature/location[@wgs84_lon != '']">
      <xsl:sort select="@wgs84_lon" data-type="number"/>
      <xsl:if test="position() = 1">
        <xsl:value-of select="@wgs84_lon - $gis_xBuffer"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:variable>

  <xsl:variable name="miny">
    <xsl:for-each select="region/features/feature/location[@wgs84_lat != '']">
      <xsl:sort select="@wgs84_lat" data-type="number"/>
      <xsl:if test="position() = 1">
        <xsl:value-of select="@wgs84_lat - $gis_yBuffer - $gis_bottom_buffer"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:variable>

  <xsl:variable name="maxx">
    <xsl:for-each select="region/features/feature/location[@wgs84_lon != '']">
      <xsl:sort select="@wgs84_lon" data-type="number" order="descending"/>
      <xsl:if test="position() = 1">
        <xsl:value-of select="@wgs84_lon + $gis_xBuffer"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:variable>

  <xsl:variable name="maxy">
    <xsl:for-each select="region/features/feature/location[@wgs84_lat != '']">
      <xsl:sort select="@wgs84_lat" data-type="number" order="descending"/>
      <xsl:if test="position() = 1">
        <xsl:value-of select="@wgs84_lat + $gis_yBuffer"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:variable>

  <xsl:apply-templates select="." mode="display_regionwide_map">
    <xsl:with-param name="minx"><xsl:value-of select="$minx"/></xsl:with-param>
    <xsl:with-param name="miny"><xsl:value-of select="$miny"/></xsl:with-param>
    <xsl:with-param name="maxx"><xsl:value-of select="$maxx"/></xsl:with-param>
    <xsl:with-param name="maxy"><xsl:value-of select="$maxy"/></xsl:with-param>
  </xsl:apply-templates>
</xsl:template>

</xsl:stylesheet>
