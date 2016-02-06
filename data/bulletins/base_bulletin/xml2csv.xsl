<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY nbsp "&#160;">
<!ENTITY quot "&#34;">
<!ENTITY deg  "&#176;">
]>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="text" indent="no" encoding="US-ASCII"/>

<xsl:template match="/regions">
  <!-- Print out a CSV file for each region. -->
  <xsl:for-each select="region">
    <!-- Technically, xsl:document is a EXSLT extension. xsltproc doesn't like
         it if I use the exsl prefix, so I changed it to the xsl namespace and
         everything works properly. Here is the namespace that I was using:
         xmlns:exsl="http://exslt.org/common"
    -->

    <xsl:variable name="filename" select="concat(@file_prefix,'.csv')"/>
    <xsl:document href="{$filename}" method="html">
      <xsl:call-template name="print_header"/>

      <xsl:apply-templates select="features/feature/location[@utm27_utmnorth != '']">
        <xsl:sort select="../@significant"/>
        <xsl:sort select="../name"/>
      </xsl:apply-templates>
    </xsl:document>
  </xsl:for-each>

  <!-- Print out a CSV file for everything. -->
  <xsl:call-template name="print_header"/>

  <xsl:apply-templates select="region/features/feature/location[@utm27_utmnorth != '']">
    <xsl:sort select="../@significant"/>
    <xsl:sort select="../name"/>
  </xsl:apply-templates>
</xsl:template>


<xsl:template match="location">
<xsl:value-of select="../@internal_id"/>
<xsl:text>,</xsl:text>
<xsl:value-of select="@id"/>
<xsl:text>,"</xsl:text>

<xsl:value-of select="../@survey_prefix"/>
<xsl:text>",</xsl:text>

<xsl:value-of select="../@survey_suffix"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="../@id"/>
<xsl:text>,</xsl:text>

<xsl:text>"</xsl:text>
<xsl:choose>
  <xsl:when test="@name != ''">
    <xsl:value-of select="@name"/>
  </xsl:when>
  <xsl:otherwise>
    <xsl:value-of select="../name"/>
  </xsl:otherwise>
</xsl:choose>
<xsl:text>",</xsl:text>

<xsl:text>"</xsl:text>
<xsl:value-of select="../aliases"/>
<xsl:text>",</xsl:text>

<xsl:value-of select="../@type"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="@coord_acquision"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="@wgs84_lon"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="@wgs84_lat"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="@utmzone"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="@utm27_utmeast"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="@utm27_utmnorth"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="@ele"/>
<xsl:text>,"</xsl:text>

<xsl:value-of select="../../../@name"/>
<xsl:text>","</xsl:text>

<xsl:value-of select="@county"/>
<xsl:text>","</xsl:text>

<xsl:value-of select="@quad"/>
<xsl:text>",</xsl:text>

<xsl:value-of select="../length"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="../depth"/>
<xsl:text>,</xsl:text>

<xsl:value-of select="../length_based_on"/>
<xsl:text>,</xsl:text>

<xsl:choose>
  <xsl:when test="../@significant = 'yes'">
    <xsl:text>yes,10,</xsl:text>
  </xsl:when>
  <xsl:when test="../@type = 'FRO'">
    <xsl:text>no,6,</xsl:text>
  </xsl:when>
  <xsl:otherwise>
    <xsl:text>no,8,</xsl:text>
  </xsl:otherwise>
</xsl:choose>

<xsl:choose>
  <xsl:when test="@access_status">
    <xsl:value-of select="@access_status"/>
  </xsl:when>
  <xsl:otherwise>
    <xsl:value-of select="../access/@status"/>
  </xsl:otherwise>
</xsl:choose>
<xsl:text>,"</xsl:text>

<xsl:value-of select="../access"/>
<xsl:text>",</xsl:text>

<xsl:value-of select="../bulletin_work/@category"/>
<xsl:text>,"</xsl:text>

<xsl:value-of select="../bulletin_work"/>
<xsl:text>","</xsl:text>

<xsl:value-of select="../desc/@author"/>

<xsl:text>"
</xsl:text>

</xsl:template>


<xsl:template name="print_header">

<xsl:text>internal_id,locid,survey_prefix,survey_suffix,survey_id,name,alternate_names,type,coord_acquision,wgs84_lon,wgs84_lat,nad27_utmzone,nad27_utmeast,nad27_utmnorth,elevation,region,county,quad,length,depth,length_based_on,significant,gislbl_pri,access enum,access descr,todo enum,todo descr,source
</xsl:text>

</xsl:template>


</xsl:stylesheet>
