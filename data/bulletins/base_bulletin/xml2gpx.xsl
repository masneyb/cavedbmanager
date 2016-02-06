<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY nbsp "&#160;">
<!ENTITY quot "&#34;">
<!ENTITY deg  "&#176;">
]>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="yes" encoding="US-ASCII"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/regions">

    <!-- Print out a GPX file for each region. -->
    <xsl:for-each select="region">
      <xsl:variable name="filename" select="concat(@file_prefix,'.gpx')"/>
      <xsl:document href="{$filename}" method="html">
        <gpx version="1.1"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xmlns="http://www.topografix.com/GPX/1/1"
             xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
          <metadata>
            <name><xsl:value-of select="@name"/></name>
          </metadata>

          <xsl:apply-templates select="features/feature/location[@wgs84_lon != '']">
            <xsl:sort select="../../@name"/>
            <xsl:sort select="name"/>
          </xsl:apply-templates>
        </gpx>
      </xsl:document>
    </xsl:for-each>


    <!-- Print out a GPX file for everything. -->
    <gpx version="1.1"
	 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	 xmlns="http://www.topografix.com/GPX/1/1"
	 xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
      <metadata>
	<name><xsl:value-of select="@name"/></name>
      </metadata>
      
      <xsl:apply-templates select="region/features/feature/location[@wgs84_lon != '']">
	<xsl:sort select="../../@name"/>
	<xsl:sort select="name"/>
      </xsl:apply-templates>
    </gpx>

  </xsl:template>

  <xsl:template match="location">
    <wpt lat="{@wgs84_lat}" lon="{@wgs84_lon}" xmlns="http://www.topografix.com/GPX/1/1">
      <xsl:variable name="name">
        <xsl:choose>
          <xsl:when test="@name">
            <xsl:value-of select="../name"/> - <xsl:value-of select="@name"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="../name"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <ele><xsl:value-of select="@ele"/></ele>
      <name><xsl:value-of select="$name"/></name>
      <cmt><xsl:value-of select="../@type"/></cmt>
      <desc><xsl:value-of select="$name"/></desc>
 
      <sym>Waypoint</sym>
    </wpt>
  </xsl:template>
  
</xsl:stylesheet>

