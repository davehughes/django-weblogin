from django.contrib.auth.models import User
from django.conf import settings
import webauth

WEBAUTH_HOST = getattr(settings, 'WEBAUTH_HOST', 'webauth.asu.edu')
WEBAUTH_PORT = getattr(settings, 'WEBAUTH_PORT', 3001)

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
        user, created = User.objects.get_or_create(username=asurite)
        return user
