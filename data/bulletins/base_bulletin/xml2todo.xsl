<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="no" encoding="US-ASCII"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="feature">
    <li>
      <em><xsl:value-of select="name"/></em>
      <xsl:text>: </xsl:text> 
      <xsl:value-of select="bulletin_work"/>
    </li>
  </xsl:template>


  <xsl:template match="region">
    <h2><xsl:value-of select="@name"/></h2>
    <ul>
      <xsl:apply-templates select="features/feature[bulletin_work != '']"/>
    </ul>
  </xsl:template>

  <xsl:template match="/regions">
    <html>
      <head>
        <title>TODO List for <xsl:value-of select="@name"/></title>
      </head>
      <body>
        <xsl:apply-templates select="region[features/feature/bulletin_work != '']"/>
      </body>
    </html>
  </xsl:template>


  <xsl:template match="/">
    <html>
      <head>
        <title>TODO List for <xsl:value-of select="regions/@name"/></title>
      </head>
      <body>
        <center>
          <h1><xsl:value-of select="regions/@name"/></h1>
        </center>

        <xsl:apply-templates select="regions"/>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
