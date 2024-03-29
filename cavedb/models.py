# SPDX-License-Identifier: Apache-2.0

import os
import re
import time
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import mark_safe
from cavedb.middleware import get_request_uri, get_valid_bulletins
import cavedb.docgen_all
import cavedb.perms
import cavedb.utils

DATUM_CHOICES = (
    ('NAD27', 'NAD27'), ('NAD83', 'NAD83'), ('WGS84', 'WGS84'),
)


COORD_SYS_CHOICES = (
    ('LATLON', 'Latitude/Longitude'), ('UTM', 'UTM'),
)


ACCESS_CHOICES = (
    ('open', 'open'), ('limited', 'limited'), ('closed', 'closed'),
    ('physically closed', 'physically_closed'), ('quarried away', 'quarried_away'),
)


class LatLonField(models.DecimalField):
    pass


class GisMap(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=255, null=True, blank=True)
    website_url = models.CharField(max_length=255, null=True, blank=True)
    license_url = models.CharField(max_length=255, null=True, blank=True)
    map_label = models.CharField(max_length=255, null=True, blank=True)
    show_all_regions_map = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'GIS Map'
        ordering = ('name',)


class GisLayer(models.Model):
    GIS_TYPE = (
        ('LINE', 'Line'), ('POLYGON', 'Polygon'), ('POINT', 'Point'), ('RASTER', 'Raster'),
    )
    LINE_TYPE = (
        ('Solid', 'Solid'), ('Dashed', 'Dashed'),
    )

    description = models.CharField(max_length=80)
    maps = models.ManyToManyField(GisMap)
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

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'GIS Layer'
        ordering = ('sort_order',)


class UtmZone(models.Model):
    utm_zone = models.IntegerField('UTM Zone')
    utm_north = models.BooleanField('North', default=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        if self.utm_north:
            return '%sN' % (self.utm_zone)

        return '%sS' % (self.utm_zone)

    class Meta:
        ordering = ('utm_zone',)
        verbose_name = 'UTM zone'


def bulletin_upload_to(instance, filename):
    return 'bulletin_attachments/%s/cover/%s' % \
           (instance.id, cavedb.utils.sanitize_filename(filename))


class Bulletin(models.Model):
    bulletin_name = models.CharField(max_length=80, unique=True)
    short_name = models.CharField(max_length=80, unique=True)
    editors = models.CharField(max_length=255)
    bw_front_cover_image = models.ImageField(upload_to=bulletin_upload_to, blank=True, null=True)
    color_front_cover_image = models.ImageField(upload_to=bulletin_upload_to, blank=True, null=True)
    back_cover_image = models.ImageField(upload_to=bulletin_upload_to, blank=True, null=True)
    bw_map1 = models.ForeignKey(GisMap, blank=True, null=True, related_name='bw_map1', \
                                verbose_name='Map #1 for the B&W bulletin',
                                on_delete=models.PROTECT)
    bw_map2 = models.ForeignKey(GisMap, blank=True, null=True, related_name='bw_map2', \
                                verbose_name='Map #2 for the B&W bulletin',
                                on_delete=models.PROTECT)
    bw_map3 = models.ForeignKey(GisMap, blank=True, null=True, related_name='bw_map3', \
                                verbose_name='Map #3 for the B&W bulletin',
                                on_delete=models.PROTECT)
    color_map1 = models.ForeignKey(GisMap, blank=True, null=True, related_name='color_map1', \
                                   verbose_name='Map #1 for the color bulletin',
                                   on_delete=models.PROTECT)
    color_map2 = models.ForeignKey(GisMap, blank=True, null=True, related_name='color_map2', \
                                   verbose_name='Map #2 for the color bulletin',
                                   on_delete=models.PROTECT)
    color_map3 = models.ForeignKey(GisMap, blank=True, null=True, related_name='color_map3', \
                                   verbose_name='Map #3 for the color bulletin',
                                   on_delete=models.PROTECT)
    title_page = models.TextField(blank=True, null=True)
    preamble_page = models.TextField(blank=True, null=True)
    contributor_page = models.TextField(blank=True, null=True)
    toc_footer = models.TextField(blank=True, null=True)
    caves_header = models.TextField("Introduction", blank=True, null=True)
    photo_index_header = models.TextField("Entra Entries in List of Photos", blank=True, null=True)
    indexed_terms = models.TextField("Indexed Terms", blank=True, null=True)
    dvd_readme = models.TextField("DVD Readme File", blank=True, null=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.short_name

    def get_bulletin_mod_date(self):
        filename = cavedb.utils.get_build_log_filename(self.id)

        try:
            mtime = os.path.getmtime(filename)
        except os.error:
            return None

        return time.localtime(mtime)

    def get_bulletin_mod_date_str(self):
        mtime = self.get_bulletin_mod_date()
        if mtime is None:
            return None

        return time.strftime("%Y-%m-%d %H:%M:%S", mtime)

    def is_document_build_in_process(self):
        lockfile = cavedb.utils.get_build_lock_file(self.id)
        return os.path.isfile(lockfile)

    def generate_doc_links(self):
        if not cavedb.perms.is_bulletin_docs_allowed(self.id):
            return ''

        base_url = '%sbulletin/%s' % (settings.MEDIA_URL, self.id)
        if self.is_document_build_in_process():
            return 'Documents are currently being regenerated. ' + \
                   'Please refresh the page in a few minutes. ' + \
                   'It will take longer if some of the GIS maps need to be regenerated.'

        regen_url = '%sbulletin/%s/generate' % (settings.MEDIA_URL, self.id)

        mtime = self.get_bulletin_mod_date_str()
        if mtime is None:
            if not cavedb.perms.is_bulletin_generation_allowed(self.id):
                return ''

            return mark_safe('This bulletin has not been generated yet. ' + \
                             'You can <a href="%s">generate</a> one now.' % (regen_url))

        if cavedb.perms.is_bulletin_generation_allowed(self.id):
            gen_txt = 'You can <a href="%s">generate</a> another one with the latest data.' % \
                      (regen_url)
        else:
            gen_txt = ''

        ret = 'The documents were generated on %s. %s<br/><br/>\n' % \
              (mtime, gen_txt) + \
              cavedb.docgen_all.get_bulletin_download_links(self) + \
              '<a href="%s/log">Build Log</a> [%s]' % \
              (base_url, cavedb.utils.get_file_size(cavedb.utils.get_build_log_filename(self.id)))

        return mark_safe(ret)

    generate_doc_links.short_description = 'Documents'
    generate_doc_links.allow_tags = True


    def show_maps(self):
        if not cavedb.perms.is_bulletin_gis_maps_allowed(self.id):
            return ''

        baseurl = '%sbulletin/%s' % (settings.MEDIA_URL, self.id)
        gismaps = GisMap.objects.all()

        ret = ''

        for gismap in gismaps:
            if not gismap.show_all_regions_map:
                continue

            localfile = cavedb.docgen_gis_maps.get_all_regions_gis_map(self.id, gismap.name)
            if not os.path.exists(localfile):
                continue

            ret += '<a href="%s/map/%s">%s All Regions</a><br/>\n' % \
                   (baseurl, gismap.name, gismap.name)

        ret += '<br/>\n'

        for region in BulletinRegion.objects.filter(bulletin__id=self.id):
            for gismap in gismaps:
                localfile = cavedb.docgen_gis_maps.get_region_gis_map(self.id, region.id, \
                                                                      gismap.name)
                if not os.path.exists(localfile):
                    continue

                ret += '<a href="%s/region/%s/map/%s">%s %s</a><br/>\n' % \
                               (baseurl, region.id, gismap.name, gismap.name, region.region_name)

            ret += '<br/>\n'

        return mark_safe(ret)


    show_maps.short_description = "GIS Maps"
    show_maps.allow_tags = True


    class Meta:
        ordering = ('bulletin_name',)


# Restrict the list of choices to items that are underneath the current bulletin
class BulletinChoice(models.ForeignKey):
    #pylint: disable=abstract-method

    def formfield(self, **kwargs):
        #pylint: disable=protected-access

        # The bulletin_id appears to be only available on the form. Since that
        # information is not available here, retrieve the bulletin_id from the
        # URL.

        regex = re.compile(r'.*?bulletin\\/(\d+)\\/')
        matches = regex.match(get_request_uri())
        if matches:
            return super().formfield(queryset=self.remote_field.model._default_manager \
                      .complex_filter({'bulletin__id': matches.group(1)}))

        return super().formfield(**kwargs)


class BulletinRegion(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.PROTECT)
    region_name = models.CharField(max_length=64)
    map_region_name = models.CharField(max_length=64, blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    show_gis_map = models.BooleanField('Show GIS Map', null=False, default=True)
    sort_order = models.IntegerField()

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return '%s - %s' % (self.bulletin.short_name, self.region_name)

    class Meta:
        verbose_name = 'region'
        ordering = ('bulletin', 'region_name',)


# Only show the user the regions that they are allowed to see.
class RegionChoice(models.ForeignKey):
    #pylint: disable=abstract-method

    def formfield(self, **kwargs):
        #pylint: disable=protected-access

        return super().formfield(queryset=self.remote_field.model._default_manager \
                   .complex_filter({'bulletin__id__in': get_valid_bulletins()}))


def gis_lineplot_upload_to(instance, filename):
    return 'bulletin_attachments/%s/gis_lineplot/%s' % \
           (instance.bulletin.id, cavedb.utils.sanitize_filename(filename))


class BulletinGisLineplot(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.PROTECT)
    attach_zip = models.FileField("Lineplot ZIP File", upload_to=gis_lineplot_upload_to)
    shp_filename = models.CharField("SHP File Name", max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)
    datum = models.CharField("Datum", max_length=64, choices=DATUM_CHOICES)
    coord_sys = models.CharField("Coordinate System", max_length=64, choices=COORD_SYS_CHOICES)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.shp_filename

    class Meta:
        ordering = ('description',)
        verbose_name = 'GIS lineplot'


class BulletinChapter(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.PROTECT)
    chapter_title = models.CharField(max_length=64)
    is_appendix = models.BooleanField('Appendix', null=False, default=False)
    sort_order = models.IntegerField()

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.chapter_title

    class Meta:
        verbose_name = 'chapter'
        ordering = ('bulletin', 'sort_order',)


class BulletinSection(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.PROTECT)
    bulletin_chapter = BulletinChoice(BulletinChapter, on_delete=models.PROTECT)
    section_title = models.CharField(max_length=64, blank=True, null=True)
    section_subtitle = models.CharField(max_length=64, blank=True, null=True)
    sort_order = models.IntegerField()
    num_columns = models.IntegerField()
    section_data = models.TextField(blank=True, null=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return '%s - %s' % (self.section_title, self.section_subtitle)

    class Meta:
        verbose_name = 'section'
        ordering = ('bulletin_chapter', 'sort_order',)


class BulletinSectionReference(models.Model):
    bulletinsection = models.ForeignKey('BulletinSection', on_delete=models.PROTECT)
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    book = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    pages = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    extra = models.CharField(max_length=255, null=True, blank=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return '%s,%s,%s,%s,%s,%s,%s,%s,%s' % \
               (self.author, self.title, self.book, self.volume, self.number, self.pages, \
                self.url, self.date, self.extra)

    class Meta:
        verbose_name = 'reference'
        ordering = ('book', 'volume', 'number', 'pages')


def bulletin_attachment_upload_to(instance, filename):
    return 'bulletin_attachments/%s/attachments/%s' % \
           (instance.bulletin.id, cavedb.utils.sanitize_filename(filename))


class BulletinAttachment(models.Model):
    bulletin = models.ForeignKey('Bulletin', on_delete=models.PROTECT)
    attachment = models.FileField(upload_to=bulletin_attachment_upload_to)
    description = models.CharField(max_length=255)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        #pylint: disable=no-member
        return self.attachment.path

    class Meta:
        ordering = ('bulletin', 'description', )
        verbose_name = 'attachment'


class StatewideDocType(models.Model):
    description = models.CharField(max_length=255, null=False, blank=False)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('description', )
        verbose_name = 'Statewide Document Type'


def statewide_doc_upload_to(instance, filename):
    return 'statewide_docs/%s/%s' % (instance.doc_type.id, cavedb.utils.sanitize_filename(filename))


class StatewideDoc(models.Model):
    doc_type = models.ForeignKey(StatewideDocType, verbose_name='Type', on_delete=models.PROTECT)
    doc = models.FileField(upload_to=statewide_doc_upload_to)
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    extra = models.CharField(max_length=255, null=True, blank=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        #pylint: disable=no-member
        return self.doc.path

    class Meta:
        ordering = ('doc_type', 'volume', 'number', 'date', )
        verbose_name = 'Statewide Document'


class County(models.Model):
    county_name = models.CharField(max_length=80, unique=True)
    survey_short_name = models.CharField(max_length=80, unique=True, null=True, blank=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.county_name

    class Meta:
        verbose_name_plural = 'counties'
        ordering = ["county_name"]


class TopoQuad(models.Model):
    quad_name = models.CharField(max_length=80, unique=True)
    county = models.ManyToManyField(County)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.quad_name

    def show_counties(self):
        #pylint: disable=no-member
        counties = []

        for county in self.county.get_queryset():
            counties.append(county.county_name)

        return ', '.join(counties)
    show_counties.short_description = "Counties"

    class Meta:
        ordering = ["quad_name"]


def feature_photo_upload_to(instance, filename):
    return 'feature_attachments/%s/photos/%s' % \
              (instance.feature.id, cavedb.utils.sanitize_filename(filename))


def photo_filename_validator(filename):
    if not filename:
        return

    lower_filename = filename.name.lower()
    if not lower_filename.endswith(('.jpg', '.png', '.pdf')):
        raise ValidationError('You can only specify file types of JPG, PNG, and PDF. If you ' + \
                              'have a non-image, then put it in the Attachments section below.')


class FeaturePhoto(models.Model):
    PHOTO_TYPE_CHOICES = (
        ('map', 'Map'), ('entrance_picture', 'Entrance Photo'),
        ('in_cave_picture', 'In-Cave Photo'), ('surface_picture', 'Surface Photo'),
        ('drawing', 'Drawing'), ('other', 'Other'),
    )

    PHOTO_SCALE_CHOICES = (
        ('column', 'Column'), ('halfpage', '1/2 Page'), ('fullpage', 'Full Page'),
    )

    ROTATE_CHOICES = (
        (0, 0), (90, 90), (180, 180), (270, 270),
    )

    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)
    filename = models.FileField('Primary Photo (color if you have it)', \
                                upload_to=feature_photo_upload_to, \
                                 validators=[photo_filename_validator])
    type = models.CharField(max_length=64, choices=PHOTO_TYPE_CHOICES)
    caption = models.CharField(max_length=255, null=True, blank=True)
    people_shown = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=64, null=True, blank=True)
    indexed_terms = models.TextField(blank=True, null=True)
    show_in_pdf = models.BooleanField('Show in PDF', null=False, default=True)
    include_on_dvd = models.BooleanField('Include on DVD', null=False, default=True)
    show_at_end = models.BooleanField('Show at End', null=False, default=False)
    rotate_degrees = models.IntegerField('Rotate X degrees in PDF', default=0, \
                                         choices=ROTATE_CHOICES)
    scale = models.CharField('Size in PDF', max_length=64, choices=PHOTO_SCALE_CHOICES, \
                             default='column')
    sort_order = models.IntegerField(default=1)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        #pylint: disable=no-member
        if self.caption:
            return '%s - %s' % (self.filename.path, self.caption)

        return '%s %s' % (self.filename.path, self.type)

    photoTypeDict = {}
    for i, photoType in enumerate(PHOTO_TYPE_CHOICES):
        photoTypeDict[photoType[0]] = i

    def get_photo_type_descr(self):
        return self.PHOTO_TYPE_CHOICES[self.photoTypeDict[self.type]][1]

    class Meta:
        ordering = ('sort_order', 'type', 'caption', )
        verbose_name = 'map / photo'
        verbose_name_plural = 'maps / photos'


class FeatureReferencedMap(models.Model):
    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)
    map = models.ForeignKey(FeaturePhoto, limit_choices_to={'type':'map'}, on_delete=models.CASCADE)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return '%s' % (self.map)

    class Meta:
        ordering = ('feature', 'map', )
        verbose_name = 'referenced map'


def feature_attachment_upload_to(instance, filename):
    return 'feature_attachments/%s/attachments/%s' % \
           (instance.feature.id, cavedb.utils.sanitize_filename(filename))


class FeatureAttachment(models.Model):
    ATTACHMENT_TYPE_CHOICES = (
        ('document', 'Document'), ('video', 'Video'), ('survey_data', 'Survey Project Files'),
        ('other', 'Other'),
    )

    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to=feature_attachment_upload_to)
    attachment_type = models.CharField(max_length=64, choices=ATTACHMENT_TYPE_CHOICES)
    user_visible_file_suffix = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=64, null=True, blank=True)
    description = models.CharField(max_length=255)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        #pylint: disable=no-member
        return self.attachment.path

    attachmentTypeDict = {}
    for i, attachmentType in enumerate(ATTACHMENT_TYPE_CHOICES):
        attachmentTypeDict[attachmentType[0]] = i

    def get_attachment_type_descr(self):
        #pylint: disable=no-member
        return self.ATTACHMENT_TYPE_CHOICES[self.attachmentTypeDict[self.type]][1]

    class Meta:
        ordering = ('feature', 'description', )
        verbose_name = 'attachment'


def feature_gis_lineplot_upload_to(instance, filename):
    return 'feature_attachments/%s/gis_lineplot/%s' % \
           (instance.feature.id, cavedb.utils.sanitize_filename(filename))


class FeatureGisLineplot(models.Model):
    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)
    attach_zip = models.FileField("Lineplot ZIP File", upload_to=feature_gis_lineplot_upload_to)
    shp_filename = models.CharField("SHP File Name", max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)
    datum = models.CharField("Datum", max_length=64, choices=DATUM_CHOICES)
    coord_sys = models.CharField("Coordinate System", max_length=64, choices=COORD_SYS_CHOICES)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.shp_filename

    class Meta:
        ordering = ('feature', 'description', )
        verbose_name = 'GIS lineplot'


class FeatureEntrance(models.Model):
    COORD_METHOD_CHOICES = (
        ('GPS', 'GPS Reading'), ('7.5\' Topo Map', '7.5 Topo Map'),
        ('Other Topo Map', 'Other Topo Map'), ('Estimate', 'Estimate'),
        ('Filled In', 'Filled In'), ('Google Earth', 'Google Earth'), ('Unknown', 'Unknown'),
    )

    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)
    entrance_name = models.CharField(max_length=64, blank=True, null=True, db_index=True, \
                                     help_text='You should enter an entrance name only if the ' +
                                     'feature has multiple entrances.')
    county = models.ForeignKey(County, db_index=True, on_delete=models.PROTECT)
    quad = models.ForeignKey(TopoQuad, db_index=True, blank=True, null=True,
                             on_delete=models.PROTECT)
    coord_acquision = models.CharField('Coord Acquired By', max_length=64, \
                                       choices=COORD_METHOD_CHOICES, blank=True, null=True)
    datum = models.CharField(max_length=64, choices=DATUM_CHOICES)
    elevation_ft = models.IntegerField('Elevation (ft)', blank=True, null=True, \
                                       help_text='Note: The elevations will be automatically ' +
                                       'updated on a nightly basis based on the Digital ' +
                                       'Elevation Models (DEM) that are loaded into the system.')
    utmzone = models.ForeignKey(UtmZone, verbose_name='UTM zone', on_delete=models.PROTECT)
    utmeast = models.IntegerField('UTM Easting', blank=True, null=True, \
                                  help_text='You only have to enter a UTM or lat/lon coordinate. ' +
                                  'The system will automatically convert the coordinate for you. ' +
                                  'Please refrain from doing any kind of transformation of the ' +
                                  'coordinate that you have so that the original coordinate is ' +
                                  'not lost.')
    utmnorth = models.IntegerField('UTM Northing', blank=True, null=True)
    latitude = LatLonField(blank=True, null=True, decimal_places=9, max_digits=13)
    longitude = LatLonField(blank=True, null=True, decimal_places=9, max_digits=13)
    access_enum = models.CharField("Access", max_length=64, choices=ACCESS_CHOICES, blank=True, \
                                   null=True, db_index=True)
    publish_location = models.BooleanField(null=False, default=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        if self.entrance_name:
            return self.entrance_name

        return 'Entrance'


    class Meta:
        ordering = ('feature', 'entrance_name', )
        verbose_name = 'entrance'


class FeatureReference(models.Model):
    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    book = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    pages = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    extra = models.CharField(max_length=255, null=True, blank=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)


    def __str__(self):
        return '%s,%s,%s,%s,%s,%s,%s,%s,%s' % \
               (self.author, self.title, self.book, self.volume, self.number, self.pages, \
                self.url, self.date, self.extra)

    class Meta:
        verbose_name = 'reference'
        ordering = ('book', 'volume', 'number', 'pages')


class Feature(models.Model):
    LENGTH_DEPTH_METHODS = (
        ('estimate', 'Estimate'), ('survey', 'Survey'),
    )

    TODO_CHOICES = (
        ('minor_field_work', 'Minor Field Work'), ('major_field_work', 'Major Field Work'),
        ('minor_computer_work', 'Minor Computer Work'), \
        ('major_computer_work', 'Major Computer Work'),
    )

    FEATURE_TYPE_CHOICES = (
        ('Cave', 'Cave'), ('Sandstone', 'Sandstone'), ('FRO', 'FRO'), ('Spring', 'Spring'), \
        ('Sinkhole', 'Sinkhole'), ('Insurgence', 'Insurgence'), ('Dig', 'Dig'),
        ('Cenote', 'Cenote'), ('Estavelle', 'Estavelle'),
    )

    name = models.CharField("Feature Name", max_length=80, db_index=True)
    alternate_names = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    additional_index_names = models.CharField(max_length=255, null=True, blank=True)
    bulletin_region = RegionChoice(BulletinRegion, db_index=True, on_delete=models.PROTECT)

    survey_county = models.ForeignKey(County, db_index=True, on_delete=models.PROTECT)
    survey_id = models.CharField("Survey ID", max_length=9, blank=True, null=True, db_index=True)
    feature_type = models.CharField("Feature Type", max_length=64, choices=FEATURE_TYPE_CHOICES, \
                                    default='cave', db_index=True)
    is_significant = models.BooleanField("Significant?", null=False, default=False)
    cave_sign_installed = models.BooleanField("Sign installed?", null=False, default=False)

    length_ft = models.IntegerField("Length (ft)", blank=True, null=True)
    depth_ft = models.IntegerField("Depth (ft)", blank=True, null=True)
    length_based_on = models.CharField("Length/Depth based on", max_length=64, \
                                       choices=LENGTH_DEPTH_METHODS, blank=True, null=True)

    source = models.CharField(max_length=80, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    internal_history = models.TextField("Additional History (not public)", blank=True, null=True)
    biology = models.TextField(blank=True, null=True)
    geology_hydrology = models.TextField('Geology / Hydrology', blank=True, null=True)
    hazards = models.TextField(blank=True, null=True)

    todo_enum = models.CharField("TODO Category", max_length=64, choices=TODO_CHOICES, blank=True, \
                                 null=True, db_index=True)
    todo_descr = models.CharField("TODO Description", max_length=255, blank=True, null=True)

    owner_name = models.CharField(max_length=80, blank=True, null=True)
    owner_address = models.CharField(max_length=80, blank=True, null=True)
    owner_phone = models.CharField(max_length=30, blank=True, null=True)

    access_enum = models.CharField("Access", max_length=64, choices=ACCESS_CHOICES, blank=True, \
                                   null=True, db_index=True)
    access_descr = models.CharField("Access Description", max_length=255, blank=True, null=True)

    create_date = models.DateTimeField("Creation Date", auto_now_add=True, editable=False, \
                                       null=True)
    mod_date = models.DateTimeField("Modification Date", auto_now=True, editable=False, null=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.survey_id)

    class Meta:
        verbose_name = 'Cave or Karst Feature'
        verbose_name_plural = 'Caves and Karst Features'
        ordering = ["name"]


class CaveUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    bulletins = models.ManyToManyField(Bulletin, \
                                       help_text='Bulletins that the user is allowed to access.')
    can_download_docs = models.BooleanField(default=True)
    can_download_gis_maps = models.BooleanField(default=True)
    can_generate_docs = models.BooleanField(default=False)

    def __str__(self):
        return '%s Profile' % (self.user)

# create a user's profile on access if none exists
User.caveuserprofile = property(lambda u: CaveUserProfile.objects.get_or_create(user=u)[0])
