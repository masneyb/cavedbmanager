<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="text" encoding="US-ASCII"/>

  <xsl:template match="/regions">
    <xsl:for-each select="region/features/feature/location[@wgs84_lon != '']">
      <xsl:value-of select="@wgs84_lat"/>
      <xsl:text>, </xsl:text>
      <xsl:value-of select="@wgs84_lon"/>
      <xsl:text>, "</xsl:text>
      <xsl:choose>
        <xsl:when test="@name">
          <xsl:value-of select="../name"/> - <xsl:value-of select="@name"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="../name"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:text>", "</xsl:text>
      <xsl:value-of select="../@id"/>
      <xsl:text>", "Number: </xsl:text>
      <xsl:value-of select="position()"/>
      <xsl:text> Height: </xsl:text>
      <xsl:value-of select="@ele"/>
      <xsl:text>", ff0000, 3
</xsl:text>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
