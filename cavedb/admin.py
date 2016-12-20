# vim: set fileencoding=UTF-8 :
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from curses.ascii import isprint, isspace
from django.contrib import admin
from django.conf import settings
from cavedb.models import *
from sys import stderr
from re import compile

###############################################################################
### Custom widgets and form fields                                          ###
###############################################################################

class CavedbCharFormField(forms.CharField):
    def clean(self, value):
        data = super(CavedbCharFormField, self).clean(value)

        if (data == None):
            return data

        data = data.encode('UTF-8')
        data = data.replace("—", "--");
        data = data.replace("“", "\"");
        data = data.replace("”", "\"");
        data = data.replace("’", "'");
        data = data.replace("‘", "'");

        try:
            return data.encode('ascii')
        except:
            raise forms.ValidationError('All data must be in ASCII format')

class CavedbLatLonFormField(forms.DecimalField):
    def clean(self, value):
        if (value == None or value == ''):
            return None

        # Check for a Lat/Lon in decimal degrees
        dec_degree = compile(r'^\-*\d{2}\.\d+$')
        if (dec_degree.match(value)):
            return value

        # Check for dd mm ss, with an optional negative sign at the beginning
        ddmmss = compile(r'^(\-*)(\d{2})\s+(\d{2})\s+(\d{2}(\.\d+)*)$')
        ddmmss_groups = ddmmss.match(value)

        if (ddmmss_groups != None):
            degrees = ddmmss_groups.group(2)
            mins = ddmmss_groups.group(3)
            secs = ddmmss_groups.group(4)

            newvalue = float(degrees) + (float(mins) / 60) + (float(secs) / 3600)
            if (ddmmss_groups.group(1) == '-'):
                newvalue = newvalue * -1;

            # FIXME - log old value to database
            print >> stderr, 'Notice: Converted coordinate %s to %s\n' % (value, newvalue)
            return str(newvalue)


        # Check for dd mm.ss, with an optional negative sign at the beginning
        ddmm = compile(r'^(\-*)(\d{2})\s+(\d{2}(\.\d+)*)$')
        ddmm_groups = ddmm.match(value)

        if (ddmm_groups != None):
            degrees = ddmm_groups.group(2)
            mins = ddmm_groups.group(3)

            newvalue = float(degrees) + (float(mins) / 60)
            if (ddmm_groups.group(1) == '-'):
                newvalue = newvalue * -1;

            # FIXME - log old value to database
            print >> stderr, 'Notice: Converted coordinate %s to %s\n' % (value, newvalue)
            return str(newvalue)

        raise forms.ValidationError('Invalid coordinate. Supported values are dd mm ss[.frac sec], dd mm.[ss] and dd.[decimal degrees]')

class CavedbModelAdmin(BaseModelAdmin):
    def __init__(self, model, admin_site):
        super(CavedbModelAdmin, self).__init__(model, admin_site)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, LatLonField):
            kwargs['form_class'] = CavedbLatLonFormField
        elif isinstance(db_field, models.CharField) or isinstance(db_field, models.TextField):
            kwargs['form_class'] = CavedbCharFormField

        return super(CavedbModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)


###############################################################################
### UTM Zone                                                                ###
##############################################################################

class UtmZoneAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('utm_zone', 'utm_north', 'create_date', 'mod_date')
    list_filter = ['utm_north', 'create_date', 'mod_date']

admin.site.register(UtmZone, UtmZoneAdmin)


###############################################################################
### Bulletin                                                                ###
###############################################################################

class BulletinRegionInline(CavedbModelAdmin, admin.TabularInline):
    model = BulletinRegion
    extra = 1

class BulletinGisLineplotInline(CavedbModelAdmin, admin.TabularInline):
    model = BulletinGisLineplot
    extra = 1

class BulletinChapterInline(CavedbModelAdmin, admin.TabularInline):
    model = BulletinChapter
    extra = 1

class BulletinSectionInline(CavedbModelAdmin, admin.TabularInline):
    model = BulletinSection
    extra = 1

class BulletinAttachmentInline(CavedbModelAdmin, admin.TabularInline):
    model = BulletinAttachment
    extra = 1

class BulletinAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('bulletin_name', 'editors', 'generate_doc_links', 'show_maps')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['bulletin_name', 'short_name', 'editors', 'bw_front_cover_image', 'color_front_cover_image',
                     'back_cover_image', 'title_page', 'preamble_page', 'contributor_page', 'toc_footer', 'caves_header',
                     'bulletincontributorsection__name', 
                     'bulletincontributorsection__header',
                     'bulletincontributorsection__footer',
                     'bulletincontributorsection__bulletincontributorname__first_name',
                     'bulletincontributorsection__bulletincontributorname__last_name',
                     'bulletinregion__region_name',
                     'bulletinchapter__chapter_title',
                     'bulletinchapter__bulletinsection__section_title',
                     'bulletinchapter__bulletinsection__section_subtitle',
                     'bulletinchapter__bulletinsection__section_data']

    fieldsets = [
       ('Bulletin', {'fields': ['bulletin_name','short_name','editors',]}),
       ('Content', {'fields': ['bw_front_cover_image', 'color_front_cover_image', 'back_cover_image', 'bw_map1', 'bw_map2',
                               'bw_map3', 'color_map1', 'color_map2', 'color_map3', 'title_page', 'preamble_page',
                               'contributor_page', 'toc_footer', 'caves_header', 'photo_index_header', 'indexed_terms',
                               'dvd_readme', ]}),
    ]

    inlines = [BulletinRegionInline, BulletinGisLineplotInline,
               BulletinChapterInline,
               BulletinSectionInline, BulletinAttachmentInline, ]
               
    def has_change_permission(self, request, obj=None):
        if (not obj):
            return super(BulletinAdmin, self).has_change_permission(request, obj)

        return is_bulletin_allowed(obj.id)
        
    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
        
    def get_queryset(self, request):
        return super(BulletinAdmin,self).get_queryset(request).filter(id__in=get_valid_bulletins())

    class Media:
        css = {
            "all": ("/media/admin/css/cavedb_bulletin.css",)
        }
        
        
admin.site.register(Bulletin, BulletinAdmin)


###############################################################################
### County                                                                  ###
###############################################################################

class CountyAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('county_name', 'survey_short_name', 'create_date', 'mod_date')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['county_name', 'survey_short_name']
    
admin.site.register(County, CountyAdmin)


###############################################################################
### Topo Quad                                                               ###
###############################################################################

class TopoQuadAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('quad_name', 'show_counties', 'create_date', 'mod_date')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['quad_name']

admin.site.register(TopoQuad, TopoQuadAdmin)


###############################################################################
### Feature                                                                 ###
###############################################################################

class FeaturePhotoInline(CavedbModelAdmin, admin.TabularInline):
    model = FeaturePhoto
    extra = 1

class FeatureReferencedMapInline(CavedbModelAdmin, admin.TabularInline):
    model = FeatureReferencedMap
    extra = 1

class FeatureGisLineplotInline(CavedbModelAdmin, admin.TabularInline):
    model = FeatureGisLineplot
    extra = 1

class FeatureAttachmentInline(CavedbModelAdmin, admin.TabularInline):
    model = FeatureAttachment
    extra = 1

class FeatureEntranceInline(CavedbModelAdmin, admin.StackedInline):
    model = FeatureEntrance
    extra = 1

class FeatureReferenceInline(CavedbModelAdmin, admin.TabularInline):
    model = FeatureReference
    extra = 1

class FeatureAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True

    list_display = ('name', 'survey_county', 'survey_id', 'feature_type',
                    'length_ft', 'depth_ft', 'todo_enum', 'todo_descr', 'access_enum')

                    # FIXME - disabled for performance reasons 'show_feature_attrs')

    list_filter = ['feature_type', 'is_significant', 'todo_enum',
                   'access_enum', 'survey_county', 'bulletin_region',
                   'cave_sign_installed', 'length_based_on',
                   'create_date', 'mod_date']

    search_fields = ['name', 'alternate_names', 'additional_index_names']
# FIXME - disabled for performance reasons
#    search_fields = ['name', 'alternate_names', 'additional_index_names', 'survey_county__county_name',
#                     'survey_id', 'source', 'description', 'history', 'internal_history', 'biology',
#                     'geology_hydrology', 'hazards', 'todo_descr',
#                     'access_descr', 'owner_name', 'owner_address',
#                     'owner_phone', 'featurephoto__filename',
#                     'featurephoto__caption', 'featureattachment__attachment',
#                     'featureattachment__description',
#                     'featuregislineplot__attach_zip',
#                     'featuregislineplot__shp_filename',
#                     'featuregislineplot__description',
#                     'featureentrance__entrance_name',
#                     'featureentrance__county__county_name',
#                     'featureentrance__quad__quad_name',
#                     'featurereference__reference']

    fieldsets = [ 
       ('Feature', {'fields': ['name', 'alternate_names', 'additional_index_names', 
                               'bulletin_region', 'survey_county', 'survey_id', 'feature_type',
                               'is_significant', 'cave_sign_installed',]}),
       ('Cave Length/Depth', {'fields': ['length_ft', 'depth_ft',
                                         'length_based_on',]}),
       ('Description', {'fields': ['source', 'description', 'history', 'internal_history',
                                   'biology', 'geology_hydrology',
                                   'hazards',]}),
       ('TODO', {'fields': ['todo_enum','todo_descr',]}),
       ('Access and Owner Information', {'fields': ['access_enum', 'access_descr', 'owner_name',
                              'owner_address', 'owner_phone',]}),
    ]

    inlines = [FeatureReferenceInline, FeaturePhotoInline, 
               FeatureReferencedMapInline, FeatureGisLineplotInline, 
               FeatureAttachmentInline, FeatureEntranceInline]

    def has_change_permission(self, request, obj=None):
        if (not obj):
            return super(FeatureAdmin, self).has_change_permission(request, obj)

        return is_bulletin_allowed(obj.bulletin_region.bulletin.id)
        
    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
        
    def get_queryset(self, request):
        return super(FeatureAdmin,self).get_queryset(request).filter(bulletin_region__bulletin__in=get_valid_bulletins())

    class Media:
        css = {
            "all": ("/media/admin/css/cavedb_feature.css",)
        }
        
admin.site.register(Feature, FeatureAdmin)


###############################################################################
### Cave User Profile                                                       ###
###############################################################################

class CaveUserProfileInline(admin.StackedInline):
    model = CaveUserProfile
    extra = 1
    max_num = 1
    
class CaveUserProfileAdmin(UserAdmin):
    inlines = [CaveUserProfileInline,]
    
admin.site.unregister(User)
admin.site.register(User, CaveUserProfileAdmin)


###############################################################################
### GIS                                                                     ###
###############################################################################

class GisLayerAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('description', 'display', 'table_name', 'max_scale', 'type', 'color', 'label_item', 'font_color', 'font_size', 'line_type', 'symbol', 'symbol_size', 'sort_order')
    list_filter = ['display', 'type', 'maps']
    search_fields = ['description', 'source', 'table_name', 'filename', 'label_item', 'symbol', 'notes']

    fieldsets = [ 
       ('Description', {'fields': ['description', 'maps', 'source', 'table_name', 'filename', 'display', 'max_scale', 'type', 'color', 'notes', 'sort_order']}),
       ('Label', {'fields': ['label_item', 'font_color', 'font_size']}),
       ('Symbol', {'fields': ['symbol', 'symbol_size', 'line_type']}),
    ]
 
admin.site.register(GisLayer, GisLayerAdmin)


class GisMapAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'description', 'map_label', 'website_url', 'license_url')

    fieldsets = [ 
       ('Description', {'fields': ['name', 'description', 'map_label', 'website_url', 'license_url']}),
    ]
 
admin.site.register(GisMap, GisMapAdmin)


