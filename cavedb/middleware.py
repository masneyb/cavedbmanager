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

# cciw/middleware/threadlocals.py
# http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser

import threading
from django.contrib.auth.models import AnonymousUser

THREAD_LOCALS = threading.local()

def get_current_user():
    return getattr(THREAD_LOCALS, 'user', None)

def get_request_uri():
    return getattr(THREAD_LOCALS, 'request_uri', None)

def get_valid_bulletins():
    return getattr(THREAD_LOCALS, 'valid_bulletins', [])

class ThreadLocals(object):
    #pylint: disable=too-few-public-methods

    # Middleware that gets various objects from the
    # request object and saves them in thread local storage.

    def process_request(self, request):
        #pylint: disable=no-self-use

        THREAD_LOCALS.user = getattr(request, 'user', None)
        THREAD_LOCALS.request_uri = request.META.get('PATH_INFO')

        valid_bulletins = [1]
        user = get_current_user()

        if not isinstance(user, AnonymousUser):
            for bulletin_id in user.caveuserprofile.bulletins.get_queryset():
                valid_bulletins.append(bulletin_id.id)

        THREAD_LOCALS.valid_bulletins = valid_bulletins
