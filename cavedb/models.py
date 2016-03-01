from cavedb.utils import *
from cavedb.middleware import get_request_uri, get_valid_bulletins
from django.contrib.auth.models import User
from os.path import isfile, getmtime
from time import strftime, localtime
from django.conf import settings
from django.db import models
from django import forms
from re import compile

DATUM_CHOICES = (
    ('NAD27', 'NAD27'), ('NAD83', 'NAD83'), ('WGS84', 'WGS84'),
)

COORD_SYS_CHOICES = (
    ('LATLON', 'Latitude/Longitude'), ('UTM', 'UTM'),
)

ACCESS_CHOICES = (
    ('open', 'open'), ('limited', 'limited'), ('closed', 'closed'), ('physically closed', 'physically_closed'), ('quarried away', 'quarried_away'),
)

###############################################################################
### Custom Model Fields                                                     ###
###############################################################################

class LatLonField(models.DecimalField):
    pass


###############################################################################
### GIS                                                                     ###
###############################################################################

class GisLayer(models.Model):
    GIS_TYPE = (
        ('LINE', 'Line'), ('POLYGON', 'Polygon'), ('POINT', 'Point'), ('RASTER', 'Raster'),
    )
    MAP_TYPE = (
        ('Aerial', 'Aerial'), ('Topo', 'Topo'), ('Both', 'Both'),
    )
    LINE_TYPE = (
        ('Solid', 'Solid'), ('Dashed', 'Dashed'),
    )

    description = models.CharField(max_length=80)
    show_on_maps = models.CharField(max_length=64, choices=MAP_TYPE)
    table_name = models.CharField(max_length=80, null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)
    display = models.BooleanField(default=True)
    max_scale = models.DecimalField(decimal_places=2, max_digits=11, null=True, blank=True)
    type = models.CharField("Type", max_length=64, choices=GIS_TYPE)
    color = models.CharField(max_length=80, null=True, blank=True)
    label_item = models.CharField(max_length=80, null=True, blank=True)
    font_color = models.CharField(max_length=80, null=True, blank=True)
    font_size = models.IntegerField(null=True, blank=True)
    sort_order = models.IntegerField()
    line_type = models.CharField(max_length=64, choices=LINE_TYPE, null=True, blank=True)
    symbol = models.CharField(max_length=80, null=True, blank=True)
    symbol_size = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=80)
    notes = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = 'GIS Layer'
        ordering = ('sort_order',)


class GisAerialMap(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=255, null=True, blank=True)
    website_url = models.CharField(max_length=255, null=True, blank=True)
    license_url = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'GIS Aerial Map'
        ordering = ('name',)


###############################################################################
### UTM Zone                                                                ###
###############################################################################

class UtmZone(models.Model):
    utm_zone = models.IntegerField('UTM Zone', max_length=2)
    utm_north = models.BooleanField('North', default=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        if (self.utm_north):
            return u'%sN' % (self.utm_zone)
        else:
            return u'%sS' % (self.utm_zone)

    class Meta:
        ordering = ('utm_zone',)
        verbose_name = 'UTM zone'


###############################################################################
### Bulletin models                                                         ###
###############################################################################

def CavedbBulletinUploadTo(instance, filename):
    return 'bulletin_attachments/%s/cover/%s' % (instance.id, filename)

class Bulletin(models.Model):
    bulletin_name = models.CharField(max_length=80,unique=True)
    short_name = models.CharField(max_length=80,unique=True)
    editors = models.CharField(max_length=255)
    bw_front_cover_image = models.ImageField(upload_to=CavedbBulletinUploadTo, blank=True, null=True)
    color_front_cover_image = models.ImageField(upload_to=CavedbBulletinUploadTo, blank=True, null=True)
    back_cover_image = models.ImageField(upload_to=CavedbBulletinUploadTo, blank=True, null=True)
    bw_aerial_map = models.ForeignKey(GisAerialMap, blank=True, null=True, related_name='bw_aerial_map_id', verbose_name='Aerial Map for the B&W Bulletin')
    color_aerial_map = models.ForeignKey(GisAerialMap, blank=True, null=True, related_name='color_aerial_map_id', verbose_name='Aerial Map for the Color Bulletin')
    title_page = models.TextField(blank=True, null=True)
    preamble_page = models.TextField(blank=True, null=True)
    contributor_page = models.TextField(blank=True, null=True)
    toc_footer = models.TextField(blank=True, null=True)
    caves_header = models.TextField("Introduction", blank=True, null=True)
    photo_index_header = models.TextField("Entra Entries in List of Photos", blank=True, null=True)
    indexed_terms = models.TextField("Indexed Terms", blank=True, null=True)
    dvd_readme = models.TextField("DVD Readme File", blank=True, null=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.short_name

    def get_bulletin_mod_date(self):
        filename = get_xml_filename(self.id)

        try:
            mtime = getmtime(filename)
        except Exception:
            return None

        return localtime(mtime)

    def get_bulletin_mod_date_str(self):
        mtime = self.get_bulletin_mod_date()
	if (mtime == None):
	    return None

        return strftime("%Y-%m-%d %H:%M:%S", mtime)

    def is_document_build_in_process(self):
        lockfile = '%s/bulletins/bulletin_%s/build-in-progress.lock' % (settings.MEDIA_ROOT, self.id)
        return isfile(lockfile)

    def generate_doc_links(self):
        if (not is_bulletin_docs_allowed(self.id)):
            return ''

        base_url = '%sbulletin/%s' % (settings.MEDIA_URL, self.id)
        if (self.is_document_build_in_process()):
            return 'Documents are currently being regenerated. Please check back in about 10 minutes. It will take longer if some of the GIS maps need to be regenerated. If it takes more than an hour to build the document, check the very bottom of the <a href="%s/log">build log</a> for details about what may be wrong.' % (base_url)

        regen_url = '%sbulletin/%s/generate' % (settings.MEDIA_URL, self.id)

        mtime = self.get_bulletin_mod_date_str()
        if(mtime == None):
           if (not is_bulletin_generation_allowed(self.id)):
               return ''
           else:
               return 'This bulletin has not been generated yet. You can <a href="%s">generate</a> one now.' % (regen_url)
        else:
           if (is_bulletin_generation_allowed(self.id)):
               gen_txt = 'You can <a href="%s">generate</a> another one with the latest data.' % (regen_url)
           else:
               gen_txt = ''

           return 'The documents were generated on %s. %s<br /><br />\n<a href="%s/pdf">PDF (B/W)</a> [%s]<br/><a href="%s/color_pdf">PDF (Color)</a> [%s]<br/><a href="%s/draft_pdf">Draft PDF (No images)</a> [%s]<br/><a href="%s/todo_pdf">TODO PDF</a> [%s]<br/><a href="%s/mxf">Maptech File (MXF)</a> [%s]<br/><a href="%s/csv">Spreadsheet (CSV)</a> [%s]<br/><a href="%s/kml">Google Earth (KML)</a> [%s]<br/><a href="%s/text">Text (TXT)</a> [%s]<br/><a href="%s/gpx">GPS Unit (GPX)</a> [%s]<br/><a href="%s/shp">Shapefile (SHP)</a> [%s]<br/><a href="%s/dvd">Supplemental DVD (ZIP)</a> [%s]<br/><a href="%s/xml">XML</a> [%s]<br/><a href="%s/log">Build Log</a> [%s]' % (mtime, gen_txt, base_url, get_file_size (get_pdf_filename(self.id)), base_url, get_file_size (get_color_pdf_filename(self.id)), base_url, get_file_size (get_draft_pdf_filename(self.id)), base_url, get_file_size (get_todo_pdf_filename(self.id)), base_url, get_file_size (get_mxf_filename(self.id)), base_url, get_file_size (get_csv_filename(self.id)), base_url, get_file_size (get_kml_filename(self.id)), base_url, get_file_size (get_text_filename(self.id)), base_url, get_file_size (get_gpx_filename(self.id)), base_url, get_file_size (get_shp_filename(self.id)), base_url, get_file_size (get_dvd_filename(self.id)), base_url, get_file_size (get_xml_filename(self.id)), base_url, get_file_size (get_build_log_filename(self.id)))


    generate_doc_links.short_description = 'Documents'
    generate_doc_links.allow_tags = True


    def show_topo_maps(self):
        if (not is_bulletin_gis_maps_allowed(self.id)):
            return ''

        regionStr = ''
        for region in BulletinRegion.objects.filter(bulletin__id=self.id):
            regionStr += '<a href="%sbulletin/%s/region/%s/topo_map">%s</a><br/>\n' % (settings.MEDIA_URL, self.id, region.id, region.region_name)
        return regionStr

    show_topo_maps.short_description = "Topo Maps"
    show_topo_maps.allow_tags = True


    def show_aerial_maps(self):
        if (not is_bulletin_gis_maps_allowed(self.id)):
            return ''

        regionStr = ''
        for region in BulletinRegion.objects.filter(bulletin__id=self.id):
            for aerial in GisAerialMap.objects.all():
                regionStr += '<a href="%sbulletin/%s/region/%s/aerial_map/%s">%s %s</a><br/>\n' % (settings.MEDIA_URL, self.id, region.id, aerial.name, aerial.name, region.region_name)
        return regionStr

    show_aerial_maps.short_description = "Aerial Maps"
    show_aerial_maps.allow_tags = True


    class Meta:
        ordering = ('bulletin_name',)


# FIXME - all kinds of ugliness in here
# Restrict the list of choices to items that are underneath the current bulletin
class BulletinChoice(models.ForeignKey):
    def formfield(self, **kwargs):
        # The bulletin_id appears to be only available on the form. Since that
        # information is not available here, retrieve the bulletin_id from the
        # URL.

        p = compile ('.*?bulletin\\/(\d+)\\/')
        m = p.match(get_request_uri())
	if (m != None):
            return super (BulletinChoice, self).formfield(queryset=self.rel.to._default_manager.complex_filter({'bulletin__id': m.group(1)}))
        else:
            return super (BulletinChoice, self).formfield(**kwargs)


class BulletinRegion(models.Model):
    bulletin = models.ForeignKey(Bulletin)
    region_name = models.CharField(max_length=64)
    map_region_name = models.CharField(max_length=64, blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    show_gis_map = models.BooleanField('Show GIS Map', null=False, default=True)
    sort_order = models.IntegerField()

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return u'%s - %s' % (self.bulletin.short_name, self.region_name)

    class Meta:
        verbose_name = 'region'
        ordering = ('bulletin', 'region_name',)


# FIXME - hack
# Only show the user the regions that they are allowed to see.
class RegionChoice(models.ForeignKey):
    def formfield(self, **kwargs):
        return super (RegionChoice, self).formfield(queryset=self.rel.to._default_manager.complex_filter({'bulletin__id__in': get_valid_bulletins()}))


def CavedbBulletinGislineplotUploadTo(instance, filename):
    return 'bulletin_attachments/%s/gis_lineplot/%s' % (instance.bulletin.id, filename)

class BulletinGisLineplot(models.Model):
    bulletin = models.ForeignKey(Bulletin)
    attach_zip = models.FileField("Lineplot ZIP File", upload_to=CavedbBulletinGislineplotUploadTo)
    shp_filename = models.CharField("SHP File Name", max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)
    datum = models.CharField("Datum", max_length=64, choices=DATUM_CHOICES)
    coord_sys = models.CharField("Coordinate System", max_length=64, choices=COORD_SYS_CHOICES)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.shp_filename

    class Meta:
        ordering = ('description',)
        verbose_name = 'GIS lineplot'


class BulletinChapter(models.Model):
    bulletin = models.ForeignKey(Bulletin)
    chapter_title = models.CharField(max_length=64)
    is_appendix = models.BooleanField('Appendix', null=False, default=False)
    sort_order = models.IntegerField()

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.chapter_title

    class Meta:
        verbose_name = 'chapter'
        ordering = ('bulletin', 'sort_order',)


class BulletinSection(models.Model):
    bulletin = models.ForeignKey(Bulletin)
    bulletin_chapter = BulletinChoice(BulletinChapter)
    section_title = models.CharField(max_length=64, blank=True, null=True)
    section_subtitle = models.CharField(max_length=64, blank=True, null=True)
    sort_order = models.IntegerField()
    num_columns = models.IntegerField()
    section_data = models.TextField(blank=True, null=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return u'%s - %s' % (self.section_title, self.section_subtitle)

    class Meta:
        verbose_name = 'section'
        ordering = ('bulletin_chapter', 'sort_order',)


class BulletinSectionReference(models.Model):
    bulletinsection = models.ForeignKey('BulletinSection')
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    book = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    pages = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    extra = models.CharField(max_length=255, null=True, blank=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    class Meta:
        verbose_name = 'reference'
        ordering = ('book', 'volume', 'number', 'pages')


def CavedbBulletinAttachmentUploadTo(instance, filename):
    return 'bulletin_attachments/%s/attachments/%s' % (instance.bulletin.id, filename)

class BulletinAttachment(models.Model):
    bulletin = models.ForeignKey('Bulletin')
    attachment = models.FileField(upload_to=CavedbBulletinAttachmentUploadTo)
    description = models.CharField(max_length=255)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.attachment.path

    class Meta:
        ordering = ('bulletin', 'description', )
        verbose_name = 'attachment'


###############################################################################
### County                                                                  ###
###############################################################################

class County(models.Model):
    county_name = models.CharField(max_length=80, unique=True)
    survey_short_name = models.CharField(max_length=80,unique=True, null=True, blank=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.county_name

    class Meta:
        verbose_name_plural = 'counties'
        ordering = ["county_name"]


###############################################################################
### Topo Quad                                                               ###
###############################################################################

class TopoQuad(models.Model):
    quad_name = models.CharField(max_length=80, unique=True)
    county = models.ManyToManyField(County)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.quad_name
 
    def show_counties(self):
        counties = []

        for county in self.county.get_queryset():
            counties.append(county.county_name)

        return ', '.join(counties)
    show_counties.short_description = "Counties"

    class Meta:
        ordering = ["quad_name"]


###############################################################################
### Feature                                                                 ###
###############################################################################

def CavedbFeaturePhotoUploadTo(instance, filename):
    return 'feature_attachments/%s/photos/%s' % (instance.feature.id, filename.replace(' ', '_').replace('&', 'and').replace('\'', '').replace('#',''))

class FeaturePhoto(models.Model):
    PHOTO_TYPE_CHOICES = (
        ('map', 'Map'), ('entrance_picture', 'Entrance Photo'), ('in_cave_picture', 'In-Cave Photo'), ('surface_picture', 'Surface Photo'), ('drawing', 'Drawing'), ('other', 'Other'),
    )

    PHOTO_SCALE_CHOICES = (
        ('column', 'Column'), ('halfpage', '1/2 Page'), ('fullpage', 'Full Page'),
    )

    feature = models.ForeignKey('Feature')
    filename = models.FileField('Primary Photo (color if you have it)', upload_to=CavedbFeaturePhotoUploadTo)
    secondary_filename = models.FileField('Optional Secondary Photo (b/w)', upload_to=CavedbFeaturePhotoUploadTo, null=True, blank=True)
    type = models.CharField(max_length=64, choices=PHOTO_TYPE_CHOICES)
    caption = models.CharField(max_length=255, null=True, blank=True)
    people_shown = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=64, null=True, blank=True)
    indexed_terms = models.TextField(blank=True, null=True)
    show_in_pdf = models.BooleanField('Show in PDF', null=False, default=True)
    include_on_dvd = models.BooleanField('Include on DVD', null=False, default=True)
    show_at_end = models.BooleanField('Show at End', null=False, default=False)
    rotate_degrees = models.IntegerField('Rotate X degrees in PDF', default=0)
    scale = models.CharField('Size in PDF', max_length=64, choices=PHOTO_SCALE_CHOICES, default='column')
    sort_order = models.IntegerField(default=1)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        if (self.caption != None and self.caption != ''):
            return u'%s - %s' % (self.filename.path, self.caption)
        else:
            return u'%s %s' % (self.filename.path, self.type)

    photoTypeDict = {}
    for i in range(0, len(PHOTO_TYPE_CHOICES)):
       photoTypeDict[PHOTO_TYPE_CHOICES[i][0]] = i

    def get_photo_type_descr(self):
       return self.PHOTO_TYPE_CHOICES[self.photoTypeDict[self.type]][1]

    class Meta:
        ordering = ('sort_order', 'type', 'caption', )
        verbose_name = 'map / photo'
        verbose_name_plural = 'maps / photos'


class FeatureReferencedMap(models.Model):
    feature = models.ForeignKey('Feature')
    map = models.ForeignKey(FeaturePhoto, limit_choices_to={'type':'map'})

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    class Meta:
        ordering = ('feature', 'map', )
        verbose_name = 'referenced map'


def CavedbFeatureAttachmentUploadTo(instance, filename):
    return 'feature_attachments/%s/attachments/%s' % (instance.feature.id, filename)

class FeatureAttachment(models.Model):
    ATTACHMENT_TYPE_CHOICES = (
         ('document', 'Document'), ('video', 'Video'), ('survey_data', 'Survey Project Files'), ('other', 'Other'),
    )

    feature = models.ForeignKey('Feature')
    attachment = models.FileField(upload_to=CavedbFeatureAttachmentUploadTo)
    attachment_type = models.CharField(max_length=64, choices=ATTACHMENT_TYPE_CHOICES)
    user_visible_file_suffix = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=64, null=True, blank=True)
    description = models.CharField(max_length=255)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.attachment.path

    attachmentTypeDict = {}
    for i in range(0, len(ATTACHMENT_TYPE_CHOICES)):
       attachmentTypeDict[ATTACHMENT_TYPE_CHOICES[i][0]] = i

    def get_attachment_type_descr(self):
       return self.ATTACHMENT_TYPE_CHOICES[self.attachmentTypeDict[self.type]][1]

    class Meta:
        ordering = ('feature', 'description', )
        verbose_name = 'attachment'


def CavedbFeatureGislineplotUploadTo(instance, filename):
    return 'feature_attachments/%s/gis_lineplot/%s' % (instance.feature.id, filename)

class FeatureGisLineplot(models.Model):
    feature = models.ForeignKey('Feature')
    attach_zip = models.FileField("Lineplot ZIP File", upload_to=CavedbFeatureGislineplotUploadTo)
    shp_filename = models.CharField("SHP File Name", max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)
    datum = models.CharField("Datum", max_length=64, choices=DATUM_CHOICES)
    coord_sys = models.CharField("Coordinate System", max_length=64, choices=COORD_SYS_CHOICES)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return self.shp_filename

    class Meta:
        ordering = ('feature', 'description', )
        verbose_name = 'GIS lineplot'


class FeatureEntrance(models.Model):
    COORD_METHOD_CHOICES = (
        ('GPS', 'GPS Reading'), ('7.5\' Topo Map', '7.5 Topo Map'), ('Other Topo Map', 'Other Topo Map'), ('Estimate', 'Estimate'), ('Filled In', 'Filled In'), ('Google Earth', 'Google Earth'), ('Unknown', 'Unknown'),
    )

    feature = models.ForeignKey('Feature')
    entrance_name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    county = models.ForeignKey(County, db_index=True)
    quad = models.ForeignKey(TopoQuad, db_index=True, blank=True, null=True)
    coord_acquision = models.CharField('Coord Acquired By', max_length=64, choices=COORD_METHOD_CHOICES, blank=True, null=True)
    datum = models.CharField(max_length=64, choices=DATUM_CHOICES)
    elevation_ft = models.IntegerField('Elevation (ft)', blank=True, null=True)
    utmzone = models.ForeignKey(UtmZone, verbose_name='UTM zone')
    utmeast  = models.IntegerField('UTM Easting', blank=True, null=True, help_text='Note: You only have to enter a UTM or lat/lon coordinate. The system will automatically convert the coordinate for you. Please refrain from doing any kind of transformation of the coordinate that you have so that the original coordinate is not lost.')
    utmnorth = models.IntegerField('UTM Northing', blank=True, null=True)
    latitude = LatLonField(blank=True, null=True, decimal_places=9, max_digits=13, help_text='You can specify the latitude and longitude in one of the following formats: dd mm ss[.frac secs], dd mm.frac mins or dd.frac degrees. The coordinate will be automatically converted to the format dd.frac degrees.')
    longitude = LatLonField(blank=True, null=True, decimal_places=9, max_digits=13, help_text='Make sure that you remember to put a negative sign at the beginning if the cave is in the western hemisphere.')
    access_enum = models.CharField("Access", max_length=64, choices=ACCESS_CHOICES, blank=True, null=True, db_index=True)
    publish_location = models.BooleanField(null=False, default=True)
    
    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        if (self.entrance_name != None):
            return self.entrance_name
        else:
            return u'Entrance'


    class Meta:
        ordering = ('feature', 'entrance_name', )
        verbose_name = 'entrance'


class FeatureReference(models.Model):
    feature = models.ForeignKey('Feature')
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    book = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    pages = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    extra = models.CharField(max_length=255, null=True, blank=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    class Meta:
        verbose_name = 'reference'
        ordering = ('book', 'volume', 'number', 'pages')


class Feature(models.Model):
    LENGTH_DEPTH_METHODS = (
        ('estimate', 'Estimate'), ('survey', 'Survey'),
    )

    TODO_CHOICES = (
        ('minor_field_work', 'Minor Field Work'), ('major_field_work', 'Major Field Work'),
        ('minor_computer_work', 'Minor Computer Work'), ('major_computer_work', 'Major Computer Work'),
    )

    FEATURE_TYPE_CHOICES = (
        ('Cave', 'Cave'), ('Sandstone', 'Sandstone'), ('FRO', 'FRO'), ('Spring', 'Spring'), ('Sinkhole', 'Sinkhole'), ('Insurgence', 'Insurgence'), ('Dig', 'Dig'), ('Cenote', 'Cenote'), ('Estavelle', 'Estavelle'),
    )

    name = models.CharField("Feature Name", max_length=80, db_index=True)
    alternate_names = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    additional_index_names = models.CharField(max_length=255, null=True, blank=True)
    bulletin_region = RegionChoice(BulletinRegion, db_index=True)

    survey_county = models.ForeignKey(County, db_index=True)
    survey_id = models.CharField("Survey ID", max_length=9, blank=True, null=True, db_index=True)
    feature_type = models.CharField("Feature Type", max_length=64, choices=FEATURE_TYPE_CHOICES, default='cave', db_index=True)
    is_significant = models.BooleanField("Significant?", null=False, default=False)
    cave_sign_installed = models.BooleanField("Sign installed?", null=False, default=False)

    length_ft = models.IntegerField("Length (ft)", blank=True, null=True)
    depth_ft  = models.IntegerField("Depth (ft)", blank=True, null=True)
    length_based_on = models.CharField("Length/Depth based on", max_length=64, choices=LENGTH_DEPTH_METHODS, blank=True, null=True)

    source = models.CharField(max_length=80, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    internal_history = models.TextField("Additional History (not public)", blank=True, null=True)
    biology = models.TextField(blank=True, null=True)
    geology_hydrology = models.TextField('Geology / Hydrology', blank=True, null=True)
    hazards = models.TextField(blank=True, null=True)

    todo_enum = models.CharField("TODO Category", max_length=64, choices=TODO_CHOICES, blank=True, null=True, db_index=True)
    todo_descr = models.CharField("TODO Description", max_length=255, blank=True, null=True)

    owner_name = models.CharField(max_length=80, blank=True, null=True)
    owner_address = models.CharField(max_length=80, blank=True, null=True)
    owner_phone = models.CharField(max_length=30, blank=True, null=True)

    access_enum = models.CharField("Access", max_length=64, choices=ACCESS_CHOICES, blank=True, null=True, db_index=True)
    access_descr = models.CharField("Access Description", max_length=255, blank=True, null=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.survey_id)

    # FIXME - not shown
    def show_feature_attrs(self):
        ret = {}

        if (self.is_significant):
            ret['Significant Cave'] = 1

        for photo in FeaturePhoto.objects.filter(feature__id=self.id):
            ret[photo.get_photo_type_descr()] = 1

        for attachment in FeatureAttachment.objects.filter(feature__id=self.id):
            ret[attachment.get_attachment_type_descr()] = 1

        if (FeatureReferencedMap.objects.filter(feature__id=self.id).count() > 0):
            ret['Referenced Map'] = 1

        if (FeatureGisLineplot.objects.filter(feature__id=self.id).count() > 0):
            ret['GIS Lineplot'] = 1

        keys = ret.keys()
        keys.sort()
        return ', '.join(keys)
    show_feature_attrs.short_description = 'Attributes'


    class Meta:
        ordering = ["name"]


###############################################################################
### Cave User Profile                                                       ###
###############################################################################

class CaveUserProfile(models.Model):
    user = models.OneToOneField(User)
    bulletins = models.ManyToManyField(Bulletin, help_text='Select the bulletins the user is allowed to edit. ')
    can_download_docs = models.BooleanField(default=True)
    can_download_gis_maps = models.BooleanField(default=True)
    can_generate_docs = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s Profile' % (self.user)


