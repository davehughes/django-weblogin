from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect

WEBLOGIN_HOST = getattr(settings, 'WEBLOGIN_HOST')
WEBAUTH_TOKEN_COOKIE = getattr(settings, 'WEBAUTH_TOKEN_COOKIE', 'ASUWEBAUTH')

def login(request):
    '''
    Attempts to log the current session user in locally by reading their
    webauth token and authenticating with the verify service.  If a valid token
    is not provided (or if a corresponding user is not found), we will redirect
    to the weblogin 'login' page.

    Requires the WebauthBackend to be set in settings.AUTHENTICATION_BACKENDS.
    '''
    user = auth.authenticate(token=request.COOKIES.get(WEBAUTH_TOKEN_COOKIE),
                             ip=request.META.get('REMOTE_ADDR'))
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect(request.GET.get('next', '/'))
    else:
        return_page = request.build_absolute_uri()
        return HttpResponseRedirect('%s?%s=%s' % (WEBLOGIN_HOST, 
                                                  'callapp', 
                                                  return_page))

def logout(request):
    '''
    Logs the current user out locally and redirects to the weblogin 'logout'
    page.
    '''
    auth.logout(request)
    return_page = request.build_absolute_uri(request.GET.get('next', '/'))
    return http.HttpResponseRedirect('%s?%s=%s' % (WEBLOGIN_HOST,
                                                   'onLogoutURL',
                                                   return_page))
