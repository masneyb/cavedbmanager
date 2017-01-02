# Copyright 2007-2016 Brian Masney <masneyb@onstation.org>
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

from django.contrib.auth.models import AnonymousUser
from cavedb.middleware import get_current_user

def is_bulletin_generation_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_generate_docs and \
               profile.bulletins.get_queryset().filter(id=bulletin_id).count() > 0


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
