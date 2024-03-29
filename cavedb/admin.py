# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import User
import cavedb.models
import cavedb.perms
import cavedb.middleware

class UtmZoneAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('utm_zone', 'utm_north', 'create_date', 'mod_date')
    list_filter = ['utm_north', 'create_date', 'mod_date']

admin.site.register(cavedb.models.UtmZone, UtmZoneAdmin)


class BulletinRegionInline(admin.TabularInline):
    model = cavedb.models.BulletinRegion
    extra = 1


class BulletinGisLineplotInline(admin.TabularInline):
    model = cavedb.models.BulletinGisLineplot
    extra = 1


class BulletinChapterInline(admin.TabularInline):
    model = cavedb.models.BulletinChapter
    extra = 1


class BulletinSectionInline(admin.TabularInline):
    model = cavedb.models.BulletinSection
    extra = 1


class BulletinAttachmentInline(admin.TabularInline):
    model = cavedb.models.BulletinAttachment
    extra = 1


class BulletinAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('bulletin_name', 'editors', 'generate_doc_links', 'show_maps')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['bulletin_name', 'short_name', 'editors', 'bw_front_cover_image',
                     'color_front_cover_image', 'back_cover_image', 'title_page', 'preamble_page',
                     'contributor_page', 'toc_footer', 'caves_header',
                     'bulletinregion__region_name',
                     'bulletinchapter__chapter_title',
                     'bulletinchapter__bulletinsection__section_title',
                     'bulletinchapter__bulletinsection__section_subtitle',
                     'bulletinchapter__bulletinsection__section_data']

    fieldsets = [
        ('Bulletin', {'fields': ['bulletin_name', 'short_name', 'editors',]}),
        ('Content', {'fields': ['bw_front_cover_image', 'color_front_cover_image',
                                'back_cover_image', 'bw_map1', 'bw_map2', 'bw_map3', 'color_map1',
                                'color_map2', 'color_map3', 'title_page', 'preamble_page',
                                'contributor_page', 'toc_footer', 'caves_header',
                                'photo_index_header', 'indexed_terms', 'dvd_readme', ]}),
    ]

    inlines = [BulletinRegionInline, BulletinGisLineplotInline,
               BulletinChapterInline,
               BulletinSectionInline, BulletinAttachmentInline, ]

    def has_change_permission(self, request, obj=None):
        if not obj:
            return super().has_change_permission(request, obj)

        return cavedb.perms.is_bulletin_allowed(obj.id)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(id__in=cavedb.middleware.get_valid_bulletins())

    class Media:
        def __init__(self):
            pass


        css = {
            "all": ("/static/admin/css/cavedb_bulletin.css",)
        }


admin.site.register(cavedb.models.Bulletin, BulletinAdmin)


class StatewideDocTypeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('description', 'create_date', 'mod_date')
    list_filter = ['description', 'create_date', 'mod_date']

admin.site.register(cavedb.models.StatewideDocType, StatewideDocTypeAdmin)


class StatewideDocAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('doc_type', 'doc', 'title', 'volume', 'number', 'date', 'create_date',
                    'mod_date')
    list_filter = ['doc_type', 'create_date', 'mod_date']

admin.site.register(cavedb.models.StatewideDoc, StatewideDocAdmin)


class CountyAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('county_name', 'survey_short_name', 'create_date', 'mod_date')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['county_name', 'survey_short_name']

admin.site.register(cavedb.models.County, CountyAdmin)


class TopoQuadAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('quad_name', 'show_counties', 'create_date', 'mod_date')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['quad_name']

admin.site.register(cavedb.models.TopoQuad, TopoQuadAdmin)


class FeaturePhotoInline(admin.TabularInline):
    model = cavedb.models.FeaturePhoto
    extra = 1


class FeatureReferencedMapInline(admin.TabularInline):
    model = cavedb.models.FeatureReferencedMap
    extra = 1


class FeatureGisLineplotInline(admin.TabularInline):
    model = cavedb.models.FeatureGisLineplot
    extra = 1


class FeatureAttachmentInline(admin.TabularInline):
    model = cavedb.models.FeatureAttachment
    extra = 1


class FeatureEntranceInline(admin.StackedInline):
    model = cavedb.models.FeatureEntrance
    extra = 1


class FeatureReferenceInline(admin.TabularInline):
    model = cavedb.models.FeatureReference
    extra = 1


class FeatureAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ('name', 'survey_county', 'survey_id', 'feature_type',
                    'length_ft', 'depth_ft', 'todo_enum', 'todo_descr', 'access_enum')

    list_filter = ['feature_type', 'is_significant', 'todo_enum',
                   'access_enum', 'survey_county',
                   'bulletin_region__bulletin', 'bulletin_region',
                   'cave_sign_installed', 'length_based_on',
                   'create_date', 'mod_date']

    search_fields = ['name', 'alternate_names', 'additional_index_names', 'survey_id']

    fieldsets = [
        ('Feature', {'fields': ['name', 'alternate_names', 'additional_index_names',
                                'bulletin_region', 'survey_county', 'survey_id', 'feature_type',
                                'is_significant', 'cave_sign_installed',]}),
        ('Cave Length/Depth', {'fields': ['length_ft', 'depth_ft',
                                          'length_based_on',]}),
        ('Description', {'fields': ['source', 'description', 'history', 'internal_history',
                                    'biology', 'geology_hydrology',
                                    'hazards',]}),
        ('TODO', {'fields': ['todo_enum', 'todo_descr',]}),
        ('Access and Owner Information', {'fields': ['access_enum', 'access_descr', 'owner_name',
                                                     'owner_address', 'owner_phone',]}),
    ]

    inlines = [FeatureReferenceInline, FeaturePhotoInline,
               FeatureReferencedMapInline, FeatureGisLineplotInline,
               FeatureAttachmentInline, FeatureEntranceInline]

    def has_change_permission(self, request, obj=None):
        if not obj:
            return super().has_change_permission(request, obj)

        return cavedb.perms.is_bulletin_allowed(obj.bulletin_region.bulletin.id)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def get_queryset(self, request):
        return super().get_queryset(request) \
                  .filter(bulletin_region__bulletin__in=cavedb.middleware.get_valid_bulletins())

    class Media:
        def __init__(self):
            pass


        css = {
            "all": ("/static/admin/css/cavedb_feature.css",)
        }


admin.site.register(cavedb.models.Feature, FeatureAdmin)


class CaveUserProfileInline(admin.StackedInline):
    model = cavedb.models.CaveUserProfile
    extra = 1
    max_num = 1

class CaveUserProfileAdmin(UserAdmin):
    inlines = [CaveUserProfileInline,]

admin.site.unregister(User)
admin.site.register(User, CaveUserProfileAdmin)


class GisLayerAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('description', 'display', 'table_name', 'max_scale', 'type', 'color',
                    'label_item', 'font_color', 'font_size', 'line_type', 'symbol', 'symbol_size',
                    'sort_order')
    list_filter = ['display', 'type', 'maps']
    search_fields = ['description', 'source', 'table_name', 'filename', 'label_item', 'symbol',
                     'notes']

    fieldsets = [
        ('Description', {'fields': ['description', 'maps', 'source', 'table_name', 'filename',
                                    'display', 'max_scale', 'type', 'color', 'notes',
                                    'sort_order']}),
        ('Label', {'fields': ['label_item', 'font_color', 'font_size']}),
        ('Symbol', {'fields': ['symbol', 'symbol_size', 'line_type']}),
    ]

admin.site.register(cavedb.models.GisLayer, GisLayerAdmin)


class GisMapAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'description', 'map_label', 'website_url', 'license_url')

    fieldsets = [
        ('Description', {'fields': ['name', 'description', 'map_label', 'website_url',
                                    'license_url']}),
    ]

admin.site.register(cavedb.models.GisMap, GisMapAdmin)
