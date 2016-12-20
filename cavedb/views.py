from cavedb.utils import *
from curses.ascii import isalpha
from django.conf import settings
from django.http import Http404
from cavedb.models import *

###############################################################################
### Views for maps and documents                                            ###
###############################################################################

def get_bulletin_base_name(bulletin_id):
    bulletins = Bulletin.objects.filter(id=bulletin_id)
    if (bulletins.count() == 0):
        raise Http404

    base = ''
    for c in bulletins[0].short_name.lower().encode('ascii'):
        if (isalpha(c)):
            base += c
	else:
            base += '_'

    if (base == ''):
        base = 'bulletin_%s' % (bulletin_id)

    mtime = bulletins[0].get_bulletin_mod_date()
    if (mtime != None):
        disp_date = strftime("%Y%m%d-%H%M%S", mtime)
    else:
        disp_date = "UNKNOWN"

    return '%s_%s' % (base, disp_date)


def get_bulletin_remote_file(bulletin_id, extension):
    return '%s.%s' % (get_bulletin_base_name(bulletin_id), extension)


def show_pdf(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'pdf')
    return send_file(request, get_pdf_filename(bulletin_id), remotefile)


def show_color_pdf(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = '%s_color.pdf' % (get_bulletin_base_name(bulletin_id))
    return send_file(request, get_color_pdf_filename(bulletin_id), remotefile)


def show_draft_pdf(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = '%s_draft.pdf' % (get_bulletin_base_name(bulletin_id))
    return send_file(request, get_draft_pdf_filename(bulletin_id), remotefile)


def show_todo_pdf(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = '%s_todo.pdf' % (get_bulletin_base_name(bulletin_id))
    return send_file(request, get_todo_pdf_filename(bulletin_id), remotefile)


def show_kml(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'kml')
    return send_file(request, get_kml_filename(bulletin_id), remotefile)


def show_text(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'txt')
    return send_file(request, get_text_filename(bulletin_id), remotefile)


def show_gpx(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'gpx')
    return send_file(request, get_gpx_filename(bulletin_id), remotefile)


def show_csv(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'csv')
    return send_file(request, get_csv_filename(bulletin_id), remotefile)


def show_mxf(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'mxf')
    return send_file(request, get_mxf_filename(bulletin_id), remotefile)


def show_shp(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = '%s_shp_files.zip' % (get_bulletin_base_name(bulletin_id))
    return send_file(request, get_shp_filename(bulletin_id), remotefile)


def show_xml(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'xml')
    return send_file(request, get_xml_filename(bulletin_id), remotefile)


def show_dvd(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'zip')
    return send_file(request, get_dvd_filename(bulletin_id), remotefile)


def show_log(request, bulletin_id):
    if (not is_bulletin_docs_allowed(bulletin_id)):
        raise Http404

    remotefile = get_bulletin_remote_file(bulletin_id, 'txt')
    return send_file(request, get_build_log_filename(bulletin_id), remotefile)

def show_region_gis_map(request, bulletin_id, region_id, map_name):
    if (not is_bulletin_gis_maps_allowed(bulletin_id)):
        raise Http404

    localfile = '%s/bulletins/bulletin_%s/output/gis_maps/bulletin_%s_region_%s_gis_%s_map.jpg' % (settings.MEDIA_ROOT, bulletin_id, bulletin_id, region_id, map_name)
    return send_file(request, localfile, None)


###############################################################################
### Views for various attachment types                                      ###
###############################################################################

def do_show_bulletin_attachment(request, bulletin_id, localfile, filename):
    if (not is_bulletin_allowed(bulletin_id)):
        raise Http404

    if not isfile(localfile):
        raise Http404

    return send_file(request, localfile, filename)


def show_bulletin_cover(request, bulletin_id, filename):
    localfile = '%s/bulletin_attachments/%s/cover/%s' % (settings.MEDIA_ROOT, bulletin_id, filename)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, filename)


def show_bulletin_attachment(request, bulletin_id, filename):
    localfile = '%s/bulletin_attachments/%s/attachments/%s' % (settings.MEDIA_ROOT, bulletin_id, filename)
    print 'Local is %s' % (localfile)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, filename)


def show_bulletin_gis_lineplot(request, bulletin_id, filename):
    localfile = '%s/bulletin_attachments/%s/gis_lineplot/%s' % (settings.MEDIA_ROOT, bulletin_id, filename)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, filename)


def get_feature_bulletin_id(feature_id):
    features = Feature.objects.filter(id=feature_id)
    if (features.count() == 0):
        raise Http404

    return features[0].bulletin_region.bulletin.id


def show_feature_photo(request, feature_id, filename):
    localfile = '%s/feature_attachments/%s/photos/%s' % (settings.MEDIA_ROOT, feature_id, filename)
    return do_show_bulletin_attachment(request, get_feature_bulletin_id(feature_id), localfile, filename)


def show_feature_attachment(request, feature_id, filename):
    localfile = '%s/feature_attachments/%s/attachments/%s' % (settings.MEDIA_ROOT, feature_id, filename)
    return do_show_bulletin_attachment(request, get_feature_bulletin_id(feature_id), localfile, filename)


def show_feature_gis_lineplot(request, feature_id, filename):
    localfile = '%s/feature_attachments/%s/gis_lineplot/%s' % (settings.MEDIA_ROOT, feature_id, filename)
    return do_show_bulletin_attachment(request, get_feature_bulletin_id(feature_id), localfile, filename)


