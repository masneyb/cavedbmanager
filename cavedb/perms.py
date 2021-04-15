# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.models import AnonymousUser
from cavedb.middleware import get_current_user

def is_bulletin_generation_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_generate_docs and \
               profile.bulletins.get_queryset().filter(id=bulletin_id).count() > 0


def is_global_generation_allowed():
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_generate_docs


def is_bulletin_docs_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_download_docs and \
               profile.bulletins.get_queryset().filter(id=bulletin_id).count() > 0


def is_bulletin_gis_maps_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_download_gis_maps and \
               profile.bulletins.get_queryset().filter(id=bulletin_id).count() > 0


def is_bulletin_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    return get_current_user() \
               .caveuserprofile \
               .bulletins \
               .get_queryset() \
               .filter(id=bulletin_id) \
               .count() > 0
