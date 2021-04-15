# SPDX-License-Identifier: Apache-2.0

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
