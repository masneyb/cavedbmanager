from cavedb.utils import *
from os import makedirs, unlink, symlink, close, fork, setsid, chdir, system, _exit
from django.http import HttpResponseRedirect
from os.path import basename, isfile, isdir
from curses.ascii import isalpha
from django.conf import settings
from django.http import Http404
from zipfile import ZipFile
from cavedb.models import *
from popen2 import popen4
from sys import stderr, exit
from dateutil.relativedelta import *
from dateutil.parser import *
from datetime import *
from xml.sax.saxutils import escape
import hashlib
import re

try:
    import osgeo.osr
except ImportError:
    print >> stderr, 'Python GDAL library required, try `apt-get install python-gdal`'
    sys.exit(1)

def forward_to_admin(request):
    return HttpResponseRedirect('/admin/')

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


def show_region_topo_gis_map(request, bulletin_id, region_id):
    if (not is_bulletin_gis_maps_allowed(bulletin_id)):
        raise Http404

    localfile = '%s/bulletins/bulletin_%s/output/gis_maps/bulletin_%s_region_%s_gis_map.jpg' % (settings.MEDIA_ROOT, bulletin_id, bulletin_id, region_id)
    return send_file(request, localfile, None)


def show_region_aerial_gis_map(request, bulletin_id, region_id, aerial_map_name):
    if (not is_bulletin_gis_maps_allowed(bulletin_id)):
        raise Http404

    localfile = '%s/bulletins/bulletin_%s/output/gis_maps/bulletin_%s_region_%s_gis_%s_aerial_map.jpg' % (settings.MEDIA_ROOT, bulletin_id, bulletin_id, region_id, aerial_map_name)
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


###############################################################################
### Coordinate Transformation                                               ###
###############################################################################

def get_wgs84(in_srs, x, y):
    out_srs = osgeo.osr.SpatialReference()
    out_srs.SetWellKnownGeogCS('WGS84')

    ct = osgeo.osr.CoordinateTransformation(in_srs, out_srs)

    (newx, newy, newz) = ct.TransformPoint(x, y)
    return (newx, newy)


def get_nad27(in_srs, utmzone, x, y):
    out_srs = osgeo.osr.SpatialReference()
    out_srs.SetUTM(utmzone.utm_zone, utmzone.utm_north)
    out_srs.SetWellKnownGeogCS('NAD27')

    ct = osgeo.osr.CoordinateTransformation(in_srs, out_srs)

    (newx, newy, newz) = ct.TransformPoint(x, y)
    return (newx, newy)


def transform_coordinate(entrance):
   utmzone = entrance.utmzone
   nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon = '', '', '', ''

   in_srs = osgeo.osr.SpatialReference()
   in_srs.SetWellKnownGeogCS(entrance.datum.encode('ascii'))

   if (entrance.utmeast != None and entrance.utmeast != 0 and entrance.utmnorth != None and entrance.utmnorth != 0):
        in_srs.SetUTM(entrance.utmzone.utm_zone, entrance.utmzone.utm_north)

        (wgs84_lon, wgs84_lat) = get_wgs84(in_srs, int(entrance.utmeast), int(entrance.utmnorth))
        (nad27_utmeast, nad27_utmnorth) = get_nad27(in_srs, entrance.utmzone, int(entrance.utmeast), int(entrance.utmnorth))

   elif (entrance.longitude != None and entrance.longitude != 0 and entrance.latitude != None and entrance.latitude != 0):
        (wgs84_lon, wgs84_lat) = get_wgs84(in_srs, float(entrance.longitude), float(entrance.latitude))
        (nad27_utmeast, nad27_utmnorth) = get_nad27(in_srs, entrance.utmzone, float(entrance.longitude), float(entrance.latitude))

   return utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon


###############################################################################
### Date Parsing                                                            ###
###############################################################################

def get_normalized_date(str):
    # Parse lots of different date formats including:
    # Sep 21, 1997, Fall/Winter 1997, Fall 1997, etc.

    if (str == None or str == ''):
        return "0000-00-00"

    pattern = re.compile('/[\w\d]+')
    str = pattern.sub('', str)

    str = str.replace("Spring", "April");
    str = str.replace("Summer", "July");
    str = str.replace("Fall", "October");
    str = str.replace("Winter", "January");

    try:
        defaults=datetime.now()+relativedelta(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return parse(str, default=defaults)
    except:
        return "0000-00-00"


###############################################################################
### Methods for creating the bulletin documents                             ###
###############################################################################

def convert_quotes(str):
    # Directional quote support for LaTeX
    # FIXME - put this in the xml2latex.xsl stylesheet

    if (str == None):
      return ""

    str = str.strip()
    str = str.replace(" - ", " -- ")

    while (True):
      if (str.count("\"") < 2):
        break

      oldstr = str
      str = str.replace("\"", "``", 1)
      str = str.replace("\"", "''", 1)

    return escape(str)


def clean_index(input):
    # FIXME - ugly hack until Tucker County book is published
    input = input.replace("\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of Cheat River}", "\caveindex{Great Cave of Dry Fork of Cheat River}")
    input = input.replace("\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of \caveindex{Cheat River}}", "\caveindex{Great Cave of Dry Fork of Cheat River}")

    flags = re.MULTILINE | re.DOTALL | re.VERBOSE
    result = re.compile(r'(.*?)(\\caveindex{)(.*?)}(.*)', flags).match(input)
    if (not result):
        return input
    elif (re.compile(r'^\\caveindex{.*', flags).match(result.group(3))):
        value = re.sub(r'^\\caveindex{', '', result.group(3))
        return '%s%s%s%s' % (result.group(1), result.group(2), value, clean_index(result.group(4)))
    elif (not re.compile(r'^.*\\caveindex.*$', flags).match(result.group(3))):
        if (re.compile(r'^.*\\caveindex.*$', flags).match(result.group(4))):
            return '%s%s%s}%s' % (result.group(1), result.group(2), result.group(3), clean_index(result.group(4)))
        else:
            return input
    else:
        value = re.sub(r'^(.*?)\s\\caveindex{(.*)', r'\1 \2', result.group(3))
        return '%s%s' % (result.group(1), clean_index('%s%s%s' % (result.group(2), value, result.group(4))))


def finalize_index(input, indexedTerms):
    flags = re.MULTILINE | re.DOTALL | re.VERBOSE
    result = re.compile(r'(.*?)\\caveindex{(.*?)}(.*)', flags).match(input)
    if (not result):
        return input

    return '%s%s%s' % (result.group(1), indexedTerms[1][result.group(2)], finalize_index(result.group(3), indexedTerms))


def generate_index(str, indexedTerms):
    # Add terms to the index
    for term in indexedTerms[0]:
        # This appears to be quicker than doing a single regular expression
        str = str.replace('%s ' % (term), '\caveindex{%s} ' % (term))
        str = str.replace('%s.' % (term), '\caveindex{%s}.' % (term))
        str = str.replace('%s,' % (term), '\caveindex{%s},' % (term))
        str = str.replace('%s:' % (term), '\caveindex{%s}:' % (term))
        str = str.replace('%s)' % (term), '\caveindex{%s})' % (term))
        str = str.replace('%s\'' % (term), '\caveindex{%s}\'' % (term))
        #str = re.sub(r'([\s\.,]*)(' + term + r')([\s\.\,]*)', r'\1\caveindex{\2}\3', str)

    return finalize_index(clean_index(str), indexedTerms)


def convert_nl_to_para(str):
    str = convert_quotes(str)
    ret = ''
    for para in str.split('\n'):
        para = para.replace('\r', '');
        if (para == ''):
            continue

        ret = '%s<para>%s</para>' % (ret, para)

    return ret


# Add a \hbox{} around the cave and entrance names so that they appear on the 
# same line in the PDF.
def add_caption_hbox(caption, name):
    if (caption.startswith(name)):
        return caption

    return caption.replace(name, '\hbox{%s}' % (name))


def format_photo_caption(feature, caption):
    caption = add_caption_hbox(caption, feature.name)

    if (feature.alternate_names != None and feature.alternate_names != ''):
        for alias in feature.alternate_names.split(','):
            alias = alias.strip()
            if (alias != ""):
                caption = add_caption_hbox(caption, alias)

    if (feature.additional_index_names != None and feature.additional_index_names != ''):
        for alias in feature.additional_index_names.split(','):
            alias = alias.strip()
            if (alias != ""):
                caption = add_caption_hbox(caption, alias)

    for entrance in FeatureEntrance.objects.filter(feature=feature.id):
        if (entrance.entrance_name != None and entrance.entrance_name != ''):
            caption = add_caption_hbox(caption, entrance.entrance_name)

    return convert_quotes(caption)

def generate_feature(f, feature, indexedTerms):
    missing_str = ''

    todo_descr = feature.todo_descr
    todo_enum = feature.todo_enum
    if (todo_enum == None or todo_enum == ''):
        todo_enum = 'minor_computer_work'

    feature_att_str = 'type="%s" internal_id="%s"' % (feature.feature_type, feature.id)

    if (feature.is_significant):
        feature_att_str = '%s significant="yes"' % (feature_att_str)
    else:
        feature_att_str = '%s significant="no"' % (feature_att_str)


    if (feature.cave_sign_installed):
        feature_att_str = '%s cave_sign_installed="yes"' % (feature_att_str)
    else:
        feature_att_str = '%s cave_sign_installed="no"' % (feature_att_str)


    if (feature.survey_id != None and feature.survey_id != ''):
        feature_att_str = '%s survey_prefix="%s" survey_suffix="%s" id="%s%s"' % (feature_att_str, feature.survey_county.survey_short_name, feature.survey_id, feature.survey_county.survey_short_name, feature.survey_id)
    else:
        missing_str += ' ID'

    f.write('<feature %s>\n' % (feature_att_str))

    f.write('<name>%s</name>\n' % (feature.name.strip()))

    if (feature.alternate_names != None and feature.alternate_names != ''):
        for alias in feature.alternate_names.split(','):
            alias = alias.strip()
            if (alias != ""):
                f.write('<aliases>%s</aliases>\n' % (alias))

    if (feature.additional_index_names != None and feature.additional_index_names != ''):
        for alias in feature.additional_index_names.split(','):
            alias = alias.strip()
            if (alias != ""):
                f.write('<additional_index_name>%s</additional_index_name>\n' % (alias))

    # For debugging coordinate problems...
    f.flush()

    missing_coord = False
    missing_ele = False
    saw_entrance = False

    for entrance in FeatureEntrance.objects.filter(feature=feature.id):
        if (not entrance.publish_location):
            continue

        saw_entrance = True
        if (entrance.elevation_ft == None or entrance.elevation_ft == ''):
            missing_ele = True

        utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon = transform_coordinate(entrance)

        attstr = ''
        if (entrance.entrance_name != None and entrance.entrance_name != ''):
            attstr += ' name="%s"' % (entrance.entrance_name)

        if (entrance.access_enum != None and entrance.access_enum != ''):
            attstr += ' access_status="%s"' % (entrance.access_enum)

        if (entrance.coord_acquision != None and entrance.coord_acquision != ''):
            attstr += ' coord_acquision="%s"' % (entrance.coord_acquision)

        if (nad27_utmeast != '' and nad27_utmeast != 0):
            quad_name = ''
            if (entrance.quad != None):
                quad_name = entrance.quad

            f.write('<location%s id="%s" wgs84_lat="%s" wgs84_lon="%s" utmzone="%s" utm27_utmeast="%s" utm27_utmnorth="%s" ele="%s" county="%s" quad="%s"/>\n' % (attstr, entrance.id, wgs84_lat, wgs84_lon, utmzone, nad27_utmeast, nad27_utmnorth, entrance.elevation_ft, entrance.county, quad_name))
        else:
            missing_coord = True

    if (missing_coord or not saw_entrance):
        missing_str += ' GPS'
        todo_enum = 'minor_field_work'
    elif (missing_ele):
        missing_str += ' elevation'


    for attachment in FeatureAttachment.objects.filter(feature__id=feature.id):
        attrs = 'filename="%s" type="%s"' % (attachment.attachment, attachment.attachment_type)
        if (attachment.description != None and attachment.description != ''):
            attrs += ' description="%s"' % (convert_quotes(attachment.description))
        if (attachment.user_visible_file_suffix != None and attachment.user_visible_file_suffix != ''):
            attrs += ' user_visible_file_suffix="%s"' % (convert_quotes(attachment.user_visible_file_suffix))
        if (attachment.author != None and attachment.author != ''):
            attrs += ' author="%s"' % (convert_quotes(attachment.author))

        f.write('<attachment %s/>\n' % (attrs))


    has_map = False
    num_in_pdf = 1
    for photo in FeaturePhoto.objects.filter(feature__id=feature.id):
        attrs = 'id="photo%s" type="%s" scale="%s" rotate="%s" base_directory="%s" primary_filename="%s" secondary_filename="%s" sort_order="%s" show_at_end="%s" include_on_dvd="%s" show_in_pdf="%s"' % (photo.id, photo.type, photo.scale, photo.rotate_degrees, settings.MEDIA_ROOT, photo.filename, photo.secondary_filename, photo.sort_order, int(photo.show_at_end), int(photo.include_on_dvd), int(photo.show_in_pdf))

        if (photo.show_in_pdf):
          attrs += ' num_in_pdf="%s"' % (num_in_pdf)
          num_in_pdf = num_in_pdf + 1
        if (photo.caption != None and photo.caption != ''):
           attrs += ' caption="%s"' % (format_photo_caption(feature, photo.caption))
        if (photo.people_shown != None and photo.people_shown != ''):
           attrs += ' people_shown="%s"' % (convert_quotes(photo.people_shown))
        if (photo.author != None and photo.author != ''):
           attrs += ' author="%s"' % (convert_quotes(photo.author))

        f.write('<photo %s>\n' % (attrs))
        
        if (photo.indexed_terms != None and photo.indexed_terms != ''):
            for term in photo.indexed_terms.split('\n'):
                f.write('<index>%s</index>\n' % (term.strip()))

        f.write('</photo>\n')

        if (photo.type == 'map'):
            has_map = True

    for photo in FeatureReferencedMap.objects.filter(feature__id=feature.id, map__show_in_pdf=True):
        f.write('<photo ref="photo%s" type="map" show_in_pdf="1" />\n' % (photo.map.id))
        has_map = True


    if (feature.length_ft != None and feature.length_ft != ''):
        f.write('<length>%s</length>\n' % (feature.length_ft))
        if (not has_map and feature.length_ft >= 3000):
            missing_str += ' map'

    if (feature.depth_ft != None and feature.depth_ft != ''):
        f.write('<depth>%s</depth>\n' % (feature.depth_ft))

    if (feature.length_based_on != None and feature.length_based_on != ''):
        f.write('<length_based_on>%s</length_based_on>\n' % (feature.length_based_on))

    if (feature.description != None and feature.description != ''):
        if (feature.source != None and feature.source != ''):
            f.write('<desc author="%s">%s</desc>\n' % (convert_quotes(feature.source), generate_index(convert_nl_to_para(feature.description), indexedTerms)))
        else:
            f.write('<desc>%s</desc>\n' % (generate_index(convert_nl_to_para(feature.description), indexedTerms)))
    else:
        missing_str += ' description'

    if (feature.history != None and feature.history != ''):
        f.write('<history>%s</history>\n' % (generate_index(convert_quotes(feature.history), indexedTerms)))

    if (feature.internal_history != None and feature.internal_history != ''):
        f.write('<internal_history>%s</internal_history>\n' % (generate_index(convert_quotes(feature.internal_history), indexedTerms)))

    if (feature.biology != None and feature.biology != ''):
        f.write('<biology>%s</biology>\n' % (generate_index(convert_quotes(feature.biology), indexedTerms)))

    if (feature.geology_hydrology != None and feature.geology_hydrology != ''):
        f.write('<geology>%s</geology>\n' % (generate_index(convert_quotes(feature.geology_hydrology), indexedTerms)))

    if (feature.hazards != None and feature.hazards != ''):
        f.write('<hazards>%s</hazards>\n' % (generate_index(convert_quotes(feature.hazards), indexedTerms)))


    if (feature.owner_name != None and feature.owner_name != ''):
        f.write('<owner_name>%s</owner_name>\n' % (feature.owner_name))

    if (feature.owner_address != None and feature.owner_address != ''):
        f.write('<owner_address>%s</owner_address>\n' % (feature.owner_address))

    if (feature.owner_phone != None and feature.owner_phone != ''):
        f.write('<owner_phone>%s</owner_phone>\n' % (feature.owner_phone))


    for ref in FeatureReference.objects.filter(feature=feature.id):
        generate_reference_xml(f, ref)


    if (feature.access_enum != None and feature.access_enum != '' and feature.access_descr != None and feature.access_descr != ''):
        f.write('<access status="%s">%s</access>\n' % (feature.access_enum, feature.access_descr))


    if (missing_str != ''):
        missing_str = 'The following fields are missing: (%s ).' % (missing_str)

        if (todo_descr == None):
            todo_descr = missing_str
        else:
            todo_descr = '%s %s' % (todo_descr, missing_str)

    if (todo_descr != None and todo_descr != ''):
        f.write('<bulletin_work category="%s">%s</bulletin_work>\n' % (todo_enum, todo_descr))

    f.write('</feature>\n')


def get_region_gis_hash(region_id):
    m = hashlib.md5()
    for feature in Feature.objects.filter(bulletin_region__id=region_id):
        for entrance in FeatureEntrance.objects.filter(feature=feature.id):
            if (not entrance.publish_location):
                continue
            utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon = transform_coordinate(entrance)
            entranceinfo = '%s,%s,%s,%s,%s,%s,%s,%s,%s' % (feature.name, feature.feature_type, feature.is_significant, entrance.entrance_name, utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, wgs84_lon)
            m.update(entranceinfo)
    return m.hexdigest()


def get_all_regions_gis_hash(bulletin_id):
    m = hashlib.md5()
    for region in BulletinRegion.objects.filter(bulletin__id=bulletin_id):
        gis_region_hash = get_region_gis_hash(region.id)
        m.update(gis_region_hash)
    return m.hexdigest()


def generate_reference_xml(f, ref):
    hidden_in_bibliography = ref.title.startswith('unpublished trip report') or ref.title.startswith('Tucker County Speleological Survey Files') or ref.title.startswith('personal communication') or ref.title.startswith('e-mail') or ref.title.startswith('letter to') or ref.title.startswith('Trip Report in NSS Files')

    f.write('<reference author="%s" title="%s" book="%s" volume="%s" number="%s" pages="%s" url="%s" date="%s" extra="%s" parsed_date="%s" hidden_in_bibliography="%s"/>\n' % (convert_quotes(ref.author), convert_quotes(ref.title), convert_quotes(ref.book), convert_quotes(ref.volume), convert_quotes(ref.number), convert_quotes(ref.pages), convert_quotes(ref.url), convert_quotes(ref.date), convert_quotes(ref.extra), get_normalized_date(ref.date), hidden_in_bibliography))


def generate_bulletin_xml_file(bulletin, basedir):
    latex_output_dir = basedir + '/output'
    if not isdir(latex_output_dir):
        makedirs(latex_output_dir)

    filename = '%s/output/bulletin_%s.xml' % (basedir, bulletin.id)
    f = open(filename, 'w')


    indexedTerms = [], {}
    if (bulletin.indexed_terms != None):
        for searchTerm in bulletin.indexed_terms.split('\n'):
            searchTerm = convert_quotes(searchTerm.replace('\r', '').strip())
            if (searchTerm == ''):
                continue
    
            allIndexTerms = searchTerm.split(':')
            if (len(allIndexTerms) == 1):
                indexedTerms[0].append(searchTerm)
                indexedTerms[1][searchTerm] = '\index{%s}%s' % (searchTerm, searchTerm)
            else:
                replacement = ''
                for indexTerm in allIndexTerms[1:]:
                    replacement = '%s\index{%s}' % (replacement, indexTerm)
                indexedTerms[0].append(allIndexTerms[0])
                indexedTerms[1][allIndexTerms[0]] = '%s%s' % (replacement, allIndexTerms[0])


    for region in BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        for feature in Feature.objects.filter(bulletin_region__id=region.id):
            fn = feature.name.strip()
            indexedTerms[0].append(fn)
            indexedTerms[1][fn] = '\index{%s}%s' % (fn, fn)

            if (feature.alternate_names != None and feature.alternate_names != ''):
                for alias in feature.alternate_names.split(','):
                    alias = alias.strip()
                    if (alias != ""):
                        indexedTerms[0].append(alias)
                        indexedTerms[1][alias] = '\index{%s}%s' % (alias, alias)

            if (feature.additional_index_names != None and feature.additional_index_names != ''):
                for alias in feature.additional_index_names.split(','):
                    alias = alias.strip()
                    if (alias != ""):
                        indexedTerms[0].append(alias)
                        indexedTerms[1][alias] = '\index{%s}%s' % (alias, alias)

    indexedTerms[0].sort(key=lambda term: len(term), reverse=True)


    bulletin_gis_hash = get_all_regions_gis_hash(bulletin.id)

    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<regions name="%s" editors="%s" file_prefix="bulletin_%s" all_regions_gis_hash="%s">\n' % (bulletin.bulletin_name, bulletin.editors, bulletin.id, bulletin_gis_hash))

    f.write('<indexed_terms>\n')
    for term in indexedTerms[0]:
        f.write('<term search="%s" index="%s"/>\n' % (term, indexedTerms[1][term]))
    f.write('</indexed_terms>\n')

    f.write('<aerial_maps>\n')
    for aerial in GisAerialMap.objects.all():
        f.write('<aerial_map name="%s" description="%s" website_url="%s" license_url="%s"/>\n' % (convert_quotes(aerial.name), convert_quotes(aerial.description), convert_quotes(aerial.website_url), convert_quotes(aerial.license_url)))
    f.write('</aerial_maps>\n')

    generate_gis_section (basedir, f, bulletin.id)

    if (bulletin.bw_aerial_map != None and bulletin.bw_aerial_map != ''):
        f.write('<aerial_map type="black_and_white">%s</aerial_map>\n' % (bulletin.bw_aerial_map))
    if (bulletin.color_aerial_map != None and bulletin.color_aerial_map != ''):
        f.write('<aerial_map type="color">%s</aerial_map>\n' % (bulletin.color_aerial_map))

    f.write('<title_page>%s</title_page>\n' % (generate_index(convert_quotes(bulletin.title_page), indexedTerms)))

    f.write('<preamble_page>%s</preamble_page>\n' % (generate_index(convert_quotes(bulletin.preamble_page), indexedTerms)))

    if (bulletin.contributor_page != None and bulletin.contributor_page != ''):
        f.write('<contributor_page>%s</contributor_page>\n' % (generate_index(convert_quotes(bulletin.contributor_page), indexedTerms)))

    if (bulletin.toc_footer != None and bulletin.toc_footer != ''):
        f.write('<toc_footer>%s</toc_footer>\n' % (generate_index(convert_quotes(bulletin.toc_footer), indexedTerms)))

    if (bulletin.caves_header != None and bulletin.caves_header != ''):
        f.write('<caves_header>%s</caves_header>\n' % (generate_index(convert_quotes(bulletin.caves_header), indexedTerms)))

    if (bulletin.photo_index_header != None and bulletin.photo_index_header != ''):
        f.write('<photo_index_header>%s</photo_index_header>\n' % (convert_quotes(bulletin.photo_index_header)))

    if (bulletin.dvd_readme != None and bulletin.dvd_readme != ''):
        f.write('<dvd_readme>%s</dvd_readme>\n' % (escape(bulletin.dvd_readme)))

    f.write('<chapters>\n')

    for chapter in BulletinChapter.objects.filter(bulletin__id=bulletin.id):
        f.write('<chapter title="%s" is_appendix="%i">\n' % (chapter.chapter_title, chapter.is_appendix))

        for section in BulletinSection.objects.filter(bulletin_chapter__id=chapter.id):
            section_attrs = ''
            if (section.section_title != None and section.section_title != ''):
                section_attrs = '%s title="%s"' % (section_attrs, section.section_title)

            if (section.section_subtitle != None and section.section_subtitle != ''):
                section_attrs = '%s subtitle="%s"' % (section_attrs, section.section_subtitle)

            f.write('<section%s>\n' % (section_attrs))
            f.write('<text num_columns="%s">%s</text>' % (section.num_columns, generate_index(convert_quotes(section.section_data), indexedTerms)))
            for ref in BulletinSectionReference.objects.filter(bulletinsection__id=section.id):
              generate_reference_xml(f, ref)

            f.write('</section>\n')
       
        f.write('</chapter>')

    f.write('</chapters>\n')


    for region in BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        map_name = region.map_region_name
        if (map_name == None or map_name == ''):
            map_name = region.region_name

        gis_region_hash = get_region_gis_hash(region.id)

        f.write('<region name="%s" map_name="%s" file_prefix="bulletin_%s_region_%s" show_gis_map="%s" gis_hash="%s">\n' % (region.region_name, map_name, bulletin.id, region.id, int(region.show_gis_map), gis_region_hash))
        if (region.introduction != None and region.introduction != ''):
            f.write('<introduction>%s</introduction>' % (generate_index(convert_quotes(region.introduction), indexedTerms)))

        f.write('<features>\n')

        for feature in Feature.objects.filter(bulletin_region__id=region.id):
            generate_feature(f, feature, indexedTerms)

        f.write('</features>\n')
        f.write('</region>\n')


    # Write out all references together for the bibliography
    f.write('<all_references>\n')

    for region in BulletinRegion.objects.filter(bulletin__id=bulletin.id):
        for feature in Feature.objects.filter(bulletin_region__id=region.id):
            for ref in FeatureReference.objects.filter(feature=feature.id):
                generate_reference_xml(f, ref)

    for chapter in BulletinChapter.objects.filter(bulletin__id=bulletin.id):
        for section in BulletinSection.objects.filter(bulletin_chapter__id=chapter.id):
            for ref in BulletinSectionReference.objects.filter(bulletinsection__id=section.id):
              generate_reference_xml(f, ref)

    f.write('</all_references>\n')


    aliases = {}
    # Show all of the names and aliases in one place so that they can be sorted in the index
    f.write('<feature_indexes>\n')

    for feature in Feature.objects.filter(bulletin_region__bulletin__id=bulletin.id):
        f.write('<index name="%s" is_primary="1"/>\n' % (feature.name.strip()))

        if (feature.alternate_names != None and feature.alternate_names != ''):
            for alias in feature.alternate_names.split(','):
                alias = alias.strip()
                if (alias != ""):
                    if (alias in aliases):
                        aliases[alias].append(feature.id)
                    else:
                        aliases[alias] = [feature.id]

        if (feature.additional_index_names != None and feature.additional_index_names != ''):
            for alias in feature.additional_index_names.split(','):
                alias = alias.strip()
                if (alias != ""):
                    if (alias in aliases):
                        aliases[alias].append(feature.id)
                    else:
                        aliases[alias] = [feature.id]

    for alias in aliases:
        f.write('<index name="%s" is_alias="1">\n' % (alias))
        for id in aliases[alias]:
            f.write('<feature_id>%s</feature_id>\n' % (id))

        f.write('</index>\n')

    f.write('</feature_indexes>\n')

    f.write('</regions>\n')

    f.close()


def generate_makefile(bulletin_id, basedir):
    filename = '%s/Makefile' % (basedir)
    f = open(filename, 'w')

    f.write('DOCPREFIX=bulletin_%s\n' % (bulletin_id))
    f.write('DOC_BASE_DIR=$(shell pwd)\n')
    f.write('OUTPUTDIR=$(DOC_BASE_DIR)/output\n')
    f.write('TEMPLATE_BASE_DIR=$(DOC_BASE_DIR)/../base_bulletin\n')
    f.write('include $(TEMPLATE_BASE_DIR)/Makefile.include\n')

    f.close()


def close_all_fds():
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD
  
    for fd in range(3, maxfd):
        try:
            close(fd)
        except OSError:
            pass


def run_make_command(basedir):
    # Rebuild the bulletin
    pid1 = fork()
    if (pid1 == 0):
        setsid()
        close_all_fds()

        pid2 = fork()
        if (pid2 == 0):
            chdir(basedir)
            status = system('make > bulletin-build-output.txt 2>&1')

            _exit (status)
        else:
            _exit (0)


###############################################################################
### Generate GIS section                                                    ###
###############################################################################

def add_gis_lineplot(f, lineplot, gisdir, type):
    zipfile_name = '%s/%s' % (settings.MEDIA_ROOT, lineplot.attach_zip)

    if not isdir(gisdir):
        makedirs(gisdir)

    zip = ZipFile(zipfile_name, "r")
    for name in zip.namelist():
        if (name.endswith('/')):
            continue

        base = basename(name)
        if(base == ''): base = name

        gisfile = '%s/%s' % (gisdir, base)
        g = open(gisfile, 'w')
        g.write(zip.read(name))
        g.close()
    zip.close()

    f.write('<lineplot>\n<id>%s</id>\n<type>%s</type>\n<file>%s/%s</file>\n<description>%s</description>\n<datum>%s</datum>\n<coord_sys>%s</coord_sys>\n</lineplot>\n' % (lineplot.id, type, gisdir, lineplot.shp_filename, lineplot.description, lineplot.datum, lineplot.coord_sys))


def generate_gis_section (basedir, f, bulletin_id):
    legend_titles = {}

    f.write('<gis_layers>\n')

    for map in GisLayer.objects.all():
        f.write('<gis_layer>\n')
        f.write('<name>%s</name>\n' % (map.table_name))
        f.write('<show_on_maps>%s</show_on_maps>\n' % (map.show_on_maps))
        f.write('<connection_type>%s</connection_type>\n' % (settings.GIS_CONNECTION_TYPE))
        f.write('<connection>%s</connection>\n' % (settings.GIS_CONNECTION))

        if (map.filename != None and map.filename != ''):
            f.write('<data>%s</data>\n' % (map.filename))
        else:
            f.write('<data>geom from %s</data>\n' % (map.table_name))

        f.write('<display>%s</display>\n' % (int(map.display)))
        f.write('<type>%s</type>\n' % (map.type))

        if (map.label_item != None and map.label_item != ''):
            f.write('<label_item>%s</label_item>\n' % (map.label_item))

        if (map.description != None and map.description != ''):
            if (map.description not in legend_titles):
                legend_titles[map.description] = 1
                f.write('<legend first_occurance="1">%s</legend>\n' % (map.description))
            else:
                f.write('<legend first_occurance="0">%s</legend>\n' % (map.description))

        colors = map.color.split(' ')
        if (len(colors) > 2):
            f.write('<color red="%s" green="%s" blue="%s"/>\n' % (colors[0], colors[1], colors[2]))

        if (map.symbol != None and map.symbol != ''):
            f.write('<symbol>%s</symbol>\n' % (map.symbol))
            f.write('<symbol_size>%s</symbol_size>\n' % (map.symbol_size))

        if (map.max_scale != None and map.max_scale != ''):
            f.write('<max_scale>%s</max_scale>\n' % (map.max_scale))

        if (map.label_item != None and map.label_item != ''):
            colors = map.font_color.split(' ')
            f.write('<font_color red="%s" green="%s" blue="%s"/>\n' % (colors[0], colors[1], colors[2]))
            f.write('<font_size>%s</font_size>\n' % (map.font_size))

        f.write('</gis_layer>\n')


    # Expand cave and surface lineplots
    for lineplot in BulletinGisLineplot.objects.filter(bulletin__id=bulletin_id):
        name = 'bulletin_lineplot%s' % (lineplot.id)
        gisdir = '%s/bulletins/bulletin_%s/output/lineplots/bulletin_lineplot_%s' % (settings.MEDIA_ROOT, lineplot.bulletin.id, lineplot.id)
        add_gis_lineplot(f, lineplot, gisdir, 'surface')


    for lineplot in FeatureGisLineplot.objects.filter(feature__bulletin_region__bulletin__id=bulletin_id):
        name = 'feature_lineplot%s' % (lineplot.id)
        gisdir = '%s/bulletins/bulletin_%s/output/lineplots/feature_lineplot_%s' % (settings.MEDIA_ROOT, lineplot.feature.bulletin_region.bulletin.id, lineplot.id)
        add_gis_lineplot(f, lineplot, gisdir, 'underground')

    f.write('</gis_layers>\n')


###############################################################################
### View for generating the bulletin data                                   ###
###############################################################################

def generate_bulletin(request, bulletin_id):
    if (not is_bulletin_generation_allowed(bulletin_id)):
        raise Http404

    bulletins = Bulletin.objects.filter(id=bulletin_id)
    if (bulletins.count() == 0):
        raise Http404

    bulletin = bulletins[0]
    basedir = '%s/bulletins/bulletin_%s' % (settings.MEDIA_ROOT, bulletin_id)

    generate_bulletin_xml_file (bulletin, basedir)
    generate_makefile (bulletin_id, basedir)
    run_make_command (basedir)


    # This file will be removed by the build process. This is checked by the web
    # interface to see if a build is in progress.
    lockfile = '%s/bulletins/bulletin_%s/build-in-progress.lock' % (settings.MEDIA_ROOT, bulletin_id)
    f = open(lockfile, 'w')
    f.close()


    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))
 
