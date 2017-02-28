# vim: set fileencoding=utf-8
#
# Copyright 2007-2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.contrib.admin.options import BaseModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.db import models
from django import forms
from django.contrib.auth.models import User
import cavedb.models
import cavedb.perms
import cavedb.middleware

class CavedbCharFormField(forms.CharField):
    def clean(self, value):
        data = super(CavedbCharFormField, self).clean(value)

        if data is None:
            return data

        data = data.replace("—", "--")
        data = data.replace("“", "\"")
        data = data.replace("”", "\"")
        data = data.replace("’", "'")
        data = data.replace("‘", "'")

        try:
            return data.encode('ascii')
        except:
            raise forms.ValidationError('All data must be in ASCII format')


class CavedbLatLonFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(CavedbLatLonFormField, self).__init__( \
                 help_text='You can specify the latitude and longitude in one of the ' + \
                           'following formats: dd mm ss[.frac secs], dd mm.frac mins or ' + \
                            'dd.frac degrees. The coordinate will be automatically converted ' + \
                           'to the format dd.frac degrees.')

    def clean(self, value):
        try:
            return cavedb.utils.convert_lat_lon_to_decimal(value)
        except:
            raise forms.ValidationError('Invalid coordinate. Supported values are ' + \
                                        'dd mm ss[.frac sec], dd mm.[ss] and dd.[decimal degrees]')


class CavedbModelAdmin(BaseModelAdmin):
    def __init__(self, model, admin_site):
        #pylint: disable=too-many-function-args
        super(CavedbModelAdmin, self).__init__(model, admin_site)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, cavedb.models.LatLonField):
            kwargs['form_class'] = CavedbLatLonFormField
        elif isinstance(db_field, models.CharField) or isinstance(db_field, models.TextField):
            kwargs['form_class'] = CavedbCharFormField

        return super(CavedbModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class UtmZoneAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('utm_zone', 'utm_north', 'create_date', 'mod_date')
    list_filter = ['utm_north', 'create_date', 'mod_date']

admin.site.register(cavedb.models.UtmZone, UtmZoneAdmin)


class BulletinRegionInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.BulletinRegion
    extra = 1


class BulletinGisLineplotInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.BulletinGisLineplot
    extra = 1


class BulletinChapterInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.BulletinChapter
    extra = 1


class BulletinSectionInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.BulletinSection
    extra = 1


class BulletinAttachmentInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.BulletinAttachment
    extra = 1


class BulletinAdmin(CavedbModelAdmin, admin.ModelAdmin):
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
            return super(BulletinAdmin, self).has_change_permission(request, obj)

        return cavedb.perms.is_bulletin_allowed(obj.id)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def get_queryset(self, request):
        return super(BulletinAdmin, self) \
                  .get_queryset(request) \
                  .filter(id__in=cavedb.middleware.get_valid_bulletins())

    class Media:
        def __init__(self):
            pass


        css = {
            "all": ("/static/admin/css/cavedb_bulletin.css",)
        }


admin.site.register(cavedb.models.Bulletin, BulletinAdmin)


class CountyAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('county_name', 'survey_short_name', 'create_date', 'mod_date')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['county_name', 'survey_short_name']

admin.site.register(cavedb.models.County, CountyAdmin)


class TopoQuadAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('quad_name', 'show_counties', 'create_date', 'mod_date')
    list_filter = ['create_date', 'mod_date']
    search_fields = ['quad_name']

admin.site.register(cavedb.models.TopoQuad, TopoQuadAdmin)


class FeaturePhotoInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.FeaturePhoto
    extra = 1


class FeatureReferencedMapInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.FeatureReferencedMap
    extra = 1


class FeatureGisLineplotInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.FeatureGisLineplot
    extra = 1


class FeatureAttachmentInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.FeatureAttachment
    extra = 1


class FeatureEntranceInline(CavedbModelAdmin, admin.StackedInline):
    model = cavedb.models.FeatureEntrance
    extra = 1


class FeatureReferenceInline(CavedbModelAdmin, admin.TabularInline):
    model = cavedb.models.FeatureReference
    extra = 1


class FeatureAdmin(CavedbModelAdmin, admin.ModelAdmin):
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
            return super(FeatureAdmin, self).has_change_permission(request, obj)

        return cavedb.perms.is_bulletin_allowed(obj.bulletin_region.bulletin.id)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def get_queryset(self, request):
        return super(FeatureAdmin, self) \
                  .get_queryset(request) \
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


class GisLayerAdmin(CavedbModelAdmin, admin.ModelAdmin):
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


class GisMapAdmin(CavedbModelAdmin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'description', 'map_label', 'website_url', 'license_url')

    fieldsets = [
        ('Description', {'fields': ['name', 'description', 'map_label', 'website_url',
                                    'license_url']}),
    ]

admin.site.register(cavedb.models.GisMap, GisMapAdmin)

