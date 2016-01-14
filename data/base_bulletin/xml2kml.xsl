<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY nbsp "&#160;">
<!ENTITY quot "&#34;">
<!ENTITY deg  "&#176;">
]>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="yes" encoding="US-ASCII"/>
  <xsl:strip-space elements="*"/>

<!-- This transform creates a Google Earth / Maps KML file. Note -->
<!-- that coordinates are expected (as for GPX) in WGS84 datum.  -->


  <!-- Create KML document header -->
  <xsl:template match="/regions">

    <kml xmlns="http://earth.google.com/kml/2.2">
      <Document>
	<name><xsl:value-of select="@name"/></name>

	<xsl:apply-templates select="region">
	  <xsl:sort select="@name"/>
	</xsl:apply-templates>

      </Document>
    </kml>

  </xsl:template>



  <!-- Create a Folder for each region -->
  <xsl:template match="region">

    <Folder id="{@name}" xmlns="http://earth.google.com/kml/2.2">
      <name><xsl:value-of select="@name"/></name>

      <xsl:apply-templates select="features/feature[location/@wgs84_lat and @type='cave']">
	<xsl:sort select="name"/>
      </xsl:apply-templates>

    </Folder>

  </xsl:template>




  <!-- Create a Placemark for each cave -->
  <xsl:template match="feature">

    <Placemark id="{@id}" xmlns="http://earth.google.com/kml/2.2">
      <name><xsl:value-of select="name"/></name>
      <description>
	<xsl:if test="length != ''">
	  Length: <xsl:value-of select="length"/>&apos; &lt;br/&gt;
	</xsl:if>
	<xsl:if test="depth != ''">
	  Depth: <xsl:value-of select="depth"/>&apos; &lt;br/&gt;
	</xsl:if>
	<xsl:value-of select="desc"/>
      </description>
      <Point>
	<coordinates><xsl:value-of select="location/@wgs84_lon"/>,<xsl:value-of select="location/@wgs84_lat"/>,<xsl:value-of select="location/@ele"/></coordinates>
      </Point>
    </Placemark>

  </xsl:template>


</xsl:stylesheet>
