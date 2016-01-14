<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="xml" indent="no" encoding="US-ASCII"/>

<xsl:template match="/regions">
<qgis projectname="" version="1.0.0-Kore" >
  <title></title>
  <mapcanvas>
    <units>degrees</units>
    <extent>
      <xmin>0</xmin>
      <ymin>0</ymin>
      <xmax>0</xmax>
      <ymax>0</ymax>
    </extent>
    <projections>1</projections>
    <destinationsrs>
      <spatialrefsys>
        <proj4>+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs </proj4>
        <srsid>3344</srsid>
        <srid>4326</srid>
        <epsg>4326</epsg>
        <description>WGS 84</description>
        <projectionacronym>longlat</projectionacronym>
        <ellipsoidacronym>WGS84</ellipsoidacronym>
        <geographicflag>true</geographicflag>
      </spatialrefsys>
    </destinationsrs>
  </mapcanvas>

  <!-- ******************************************************************** -->
  <!-- ** Legend                                                         ** -->
  <!-- ******************************************************************** -->

  <legend>
    <legendlayer open="true" checked="Qt::Checked" name="Karst Feature Locations">
      <filegroup open="false" hidden="true" >
        <legendlayerfile isInOverview="0" visible="1" layerid="karst_feature_locations20090226124159041"/>
      </filegroup>
    </legendlayer>

    <!-- Lineplots -->
    <xsl:for-each select="gis_layers/lineplot">
      <legendlayer open="true" checked="Qt::Checked">
        <xsl:attribute name="name">
          <xsl:value-of select="description"/>
          <xsl:text> (ID </xsl:text>
          <xsl:value-of select="id"/>
          <xsl:text>)</xsl:text>
        </xsl:attribute>

        <filegroup open="false" hidden="true" >
          <legendlayerfile isInOverview="0" visible="1">
            <xsl:attribute name="layerid">
              <xsl:text>lineplot2009022612415904</xsl:text>
              <xsl:value-of select="position()"/>
            </xsl:attribute>
          </legendlayerfile>
        </filegroup>
      </legendlayer>
    </xsl:for-each>

    <!-- Other layers -->
    <xsl:for-each select="gis_layers/gis_layer">
      <xsl:sort select="position()" data-type="number" order="descending"/>

      <legendlayer open="true" name="{name}">
        <xsl:choose>
          <xsl:when test="display='1'">
            <xsl:attribute name="checked">Qt::Checked</xsl:attribute>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="checked">Qt::Unchecked</xsl:attribute>
          </xsl:otherwise>
        </xsl:choose>

        <filegroup open="false" hidden="true" >
          <legendlayerfile isInOverview="0">
            <xsl:choose>
              <xsl:when test="display='1'">
                <xsl:attribute name="visible">1</xsl:attribute>
              </xsl:when>
              <xsl:otherwise>
                <xsl:attribute name="visible">0</xsl:attribute>
              </xsl:otherwise>
            </xsl:choose>

            <xsl:attribute name="layerid">
              <xsl:text>_public___</xsl:text>
              <xsl:value-of select="name"/>
              <xsl:text>___the_geom__sql_</xsl:text>
              <xsl:value-of select="position()"/>
            </xsl:attribute>
          </legendlayerfile>
        </filegroup>
      </legendlayer>
    </xsl:for-each>
  </legend>

  <Composer>
    <Composition paperWidth="297" paperHeight="210" />
  </Composer>


  <!-- ******************************************************************** -->
  <!-- ** Project Layers                                                 ** -->
  <!-- ******************************************************************** -->

  <projectlayers layercount="{count(gis_layers/gis_layer) + count(gis_layers/lineplot) + 1}">
    <maplayer minimumScale="0" minLabelScale="0" maxLabelScale="50000" geometry="Point" type="vector" scaleBasedLabelVisibilityFlag="1" >
      <id>karst_feature_locations20090226124159041</id>
      <datasource>output/shp/karst_feature_locations.shp</datasource>
      <layername>karst_feature_locations</layername>
      <srs>
        <spatialrefsys>
          <proj4>+proj=utm +zone=17 +ellps=clrk66 +datum=NAD27 +units=m +no_defs </proj4>
          <srsid>2097</srsid>
          <srid>26717</srid>
          <epsg>26717</epsg>
          <description>NAD27 / UTM zone 17N</description>
          <projectionacronym>utm</projectionacronym>
          <ellipsoidacronym>clrk66</ellipsoidacronym>
          <geographicflag>false</geographicflag>
        </spatialrefsys>
      </srs>
      <transparencyLevelInt>255</transparencyLevelInt>
      <provider>ogr</provider>
      <displayfield>name</displayfield>
      <label>1</label>
      <attributeactions/>
      <singlesymbol>
        <symbol>
          <lowervalue></lowervalue>
          <uppervalue></uppervalue>
          <label></label>
          <pointsymbol>hard:circle</pointsymbol>
          <pointsize>2</pointsize>
          <rotationclassificationfieldname></rotationclassificationfieldname>
          <scaleclassificationfieldname></scaleclassificationfieldname>
          <outlinecolor red="0" blue="0" green="0" />
          <fillpattern>SolidPattern</fillpattern>
          <outlinestyle>SolidLine</outlinestyle>
          <outlinewidth>0.26</outlinewidth>
          <fillcolor red="255" green="255" blue="0"/>
          <texturepath></texturepath>
        </symbol>
      </singlesymbol>
      <labelattributes>
        <label fieldname="name" text="" />
        <family fieldname="" name="Sans Serif" />
        <size fieldname="gislbl_pri" units="pt" value="" />
        <bold fieldname="" on="0" />
        <italic fieldname="" on="0" />
        <underline fieldname="" on="0" />
        <color fieldname="" red="0" blue="0" green="0" />
        <x fieldname="" />
        <y fieldname="" />
        <offset x="0" y="0" units="pt" yfieldname="" xfieldname="" />
        <angle fieldname="" value="45" auto="0" />
        <alignment fieldname="" value="right" />
        <buffercolor fieldname="" red="255" blue="255" green="255" />
        <buffersize fieldname="" units="pt" value="1" />
        <bufferenabled fieldname="" on="1" />
        <multilineenabled fieldname="" on="" />
      </labelattributes>
    </maplayer>


    <!-- Lineplots -->
    <xsl:for-each select="gis_layers/lineplot">
      <maplayer minimumScale="0" minLabelScale="0" maximumScale="100000" maxLabelScale="50000" geometry="Point" type="vector" scaleBasedLabelVisibilityFlag="1" hasScaleBasedVisibilityFlag="0">
        <id>
          <xsl:text>lineplot2009022612415904</xsl:text>
          <xsl:value-of select="position()"/>
        </id>
        <datasource><xsl:value-of select="file"/>.shp</datasource>
      <layername>shots3d</layername>

      <!-- FIXME -->
      <srs>
        <spatialrefsys>
          <proj4>+proj=utm +zone=17 +ellps=clrk66 +datum=NAD27 +units=m +no_defs </proj4>
          <srsid>2097</srsid>
          <srid>26717</srid>
          <epsg>26717</epsg>
          <description>NAD27 / UTM zone 17N</description>
          <projectionacronym>utm</projectionacronym>
          <ellipsoidacronym>clrk66</ellipsoidacronym>
          <geographicflag>false</geographicflag>
        </spatialrefsys>
      </srs>

      <transparencyLevelInt>255</transparencyLevelInt>
      <provider>ogr</provider>
      <displayfield>name</displayfield>
      <label>0</label>
      <attributeactions/>
      <singlesymbol>
        <symbol>
          <lowervalue></lowervalue>
          <uppervalue></uppervalue>
          <label></label>
          <pointsymbol>hard:circle</pointsymbol>
          <pointsize>2</pointsize>
          <rotationclassificationfieldname></rotationclassificationfieldname>
          <scaleclassificationfieldname></scaleclassificationfieldname>

          <xsl:choose>
            <xsl:when test="type='underground'">
              <outlinecolor red="255" green="0" blue="0"/>
            </xsl:when>
            <xsl:otherwise>
              <outlinecolor red="0" green="255" blue="0"/>
            </xsl:otherwise>
          </xsl:choose>

          <outlinewidth>0.52</outlinewidth>
          <outlinestyle>SolidLine</outlinestyle>
          <fillpattern>NoBrush</fillpattern>
          <texturepath></texturepath>
        </symbol>
      </singlesymbol>
    </maplayer>
    </xsl:for-each>

    <!-- Other layers -->
    <xsl:for-each select="gis_layers/gis_layer">
      <xsl:sort select="position()" data-type="number" order="descending"/>

      <maplayer minimumScale="0" minLabelScale="0" maxLabelScale="50000" geometry="Point" type="vector" scaleBasedLabelVisibilityFlag="1" >
        <xsl:if test="max_scale != ''">
          <xsl:attribute name="maximumScale"><xsl:value-of select="max_scale"/></xsl:attribute>
          <xsl:attribute name="hasScaleBasedVisibilityFlag">1</xsl:attribute>
        </xsl:if>

        <id>
          <xsl:text>_public___</xsl:text>
          <xsl:value-of select="name"/>
          <xsl:text>___the_geom__sql_</xsl:text>
          <xsl:value-of select="position()"/>
        </id>
        <datasource>
          <xsl:text>dbname='caves' table="</xsl:text>
          <xsl:value-of select="name"/>
          <xsl:text>" (the_geom) sql=</xsl:text>
        </datasource>
      <layername><xsl:value-of select="name"/></layername>
      <srs>
        <spatialrefsys>
          <proj4>+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs </proj4>
          <srsid>3344</srsid>
          <srid>4326</srid>
          <epsg>4326</epsg>
          <description>WGS 84</description>
          <projectionacronym>longlat</projectionacronym>
          <ellipsoidacronym>WGS84</ellipsoidacronym>
          <geographicflag>true</geographicflag>
        </spatialrefsys>
      </srs>
      <transparencyLevelInt>255</transparencyLevelInt>
      <provider>postgres</provider>
      <displayfield>name</displayfield>

      <xsl:choose>
        <xsl:when test="label_item">
          <label>1</label>
        </xsl:when>
        <xsl:otherwise>
          <label>0</label>
        </xsl:otherwise>
      </xsl:choose>

      <attributeactions/>
      <singlesymbol>
        <symbol>
          <lowervalue></lowervalue>
          <uppervalue></uppervalue>
          <label></label>
          <pointsymbol>hard:circle</pointsymbol>
          <pointsize>2</pointsize>
          <rotationclassificationfieldname></rotationclassificationfieldname>
          <scaleclassificationfieldname></scaleclassificationfieldname>

          <xsl:choose>
            <xsl:when test="type='LINE'">
              <outlinecolor red="{color/@red}" green="{color/@green}" blue="{color/@blue}"/>
              <fillpattern>NoBrush</fillpattern>
            </xsl:when>
            <xsl:otherwise>
              <outlinecolor red="0" blue="0" green="0" />
              <fillpattern>SolidPattern</fillpattern>
            </xsl:otherwise>
          </xsl:choose>

          <outlinestyle>SolidLine</outlinestyle>
          <outlinewidth><xsl:value-of select="symbol_size * 0.26"/></outlinewidth>
          <fillcolor red="{color/@red}" green="{color/@green}" blue="{color/@blue}"/>
          <texturepath></texturepath>
        </symbol>
      </singlesymbol>

      <xsl:if test="label_item">
        <labelattributes>
          <label fieldname="{label_item}" text="" />
          <family fieldname="" name="Sans Serif" />
          <size fieldname="" units="pt" value="{font_size}" />
          <bold fieldname="" on="0" />
          <italic fieldname="" on="0" />
          <underline fieldname="" on="0" />
          <color fieldname="" red="{font_color/@red}" blue="{font_color/@blue}" green="{font_color/@green}" />
          <x fieldname="" />
          <y fieldname="" />
          <offset x="0" y="0" units="pt" yfieldname="" xfieldname="" />
          <angle fieldname="" value="0" auto="0" />
          <alignment fieldname="" value="center" />
          <buffercolor fieldname="" red="255" blue="255" green="255" />
          <buffersize fieldname="" units="pt" value="1" />
          <bufferenabled fieldname="" on="1" />
          <multilineenabled fieldname="" on="" />
        </labelattributes>
      </xsl:if>
    </maplayer>
    </xsl:for-each>
  </projectlayers>

  <properties>
    <Gui>
      <SelectionColorBluePart type="int" >0</SelectionColorBluePart>
      <CanvasColorGreenPart type="int" >255</CanvasColorGreenPart>
      <CanvasColorRedPart type="int" >255</CanvasColorRedPart>
      <SelectionColorRedPart type="int" >255</SelectionColorRedPart>
      <SelectionColorGreenPart type="int" >255</SelectionColorGreenPart>
      <CanvasColorBluePart type="int" >255</CanvasColorBluePart>
    </Gui>
    <PositionPrecision>
      <DecimalPlaces type="int" >2</DecimalPlaces>
      <Automatic type="bool" >true</Automatic>
    </PositionPrecision>
  </properties>
</qgis>

</xsl:template>
</xsl:stylesheet>
