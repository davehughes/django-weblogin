from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
import webauth

WEBAUTH_HOST = getattr(settings, 'WEBAUTH_HOST', 'webauth.asu.edu')
WEBAUTH_PORT = getattr(settings, 'WEBAUTH_PORT', 3001)
WEBAUTH_TOKEN_COOKIE = getattr(settings, 'WEBAUTH_TOKEN_COOKIE', 'ASUWEBAUTH')

class WebLoginBackend(object):
    '''
    Django authentication backend that takes a webauth token and user IP 
    address and calls the webauth 'verify' service to authenticate the user and
    retrieve their ASURITE, which is then used to look up a local user 
    account to authenticate.
    '''
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False
    
    def authenticate(self, token=None, ip=None):
        if not token: 
            return None
        try:
            verifier = webauth.Verifier(WEBAUTH_HOST, WEBAUTH_PORT)
            vresult = verifier.verify(token, ip)
            asurite = vresult['principal']
            return self.get_user_with_asurite(asurite)
        except webauth.NotAuthenticatedError as e:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_with_asurite(self, asurite):
        '''
        Bare-bones creation/retrieval of a user based on single sign-on ID.
        This is a prime candidate for customization in an inheriting class!
        '''
        user, created = User.objects.get_or_create(username=asurite,
                                                   defaults={ 'password': '!' })
        return user

class WebLoginSSOMiddleware(object):
    '''
    Implement single sign-on for users who authenticated with an external
    site.  Checks to see that if the user is already authenticated with 
    Webauth and logs them into the system if so. 
    
    This must come after Django's AuthenticationMiddleware in the 
    middleware stack.
    '''
    def process_request(self, request):
        token = request.COOKIES.get(WEBAUTH_TOKEN_COOKIE)
        if not token:
            logout(request)
        elif not request.user.is_authenticated():
            user = authenticate(token=token, ip=request.META.get('REMOTE_ADDR'))
            if user:
                login(request, user)
        return None

