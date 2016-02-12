# cciw/middleware/threadlocals.py
# http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser

from django.contrib.auth.models import AnonymousUser
import threading

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def get_request_uri():
    return getattr(_thread_locals, 'request_uri', None)

def get_valid_bulletins():
    return getattr(_thread_locals, 'valid_bulletins', [])

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        _thread_locals.request_uri = request.META.get('PATH_INFO')

        valid_bulletins = [1]
        user = get_current_user()

        if (not isinstance(user, AnonymousUser)):
            for id in user.caveuserprofile.bulletins.get_queryset():
                valid_bulletins.append(id.id)

        _thread_locals.valid_bulletins = valid_bulletins

