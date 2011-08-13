import logging

from django.contrib.auth.models import User
from django.conf import settings
import webauth

LOG = logging.getLogger(__name__)

WEBAUTH_HOST = getattr(settings, 'WEBAUTH_HOST')
WEBAUTH_PORT = getattr(settings, 'WEBAUTH_PORT')
WEBAUTH_AUTOCREATE_USERS = getattr(settings, 'WEBAUTH_AUTOCREATE_USERS', True)

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
            return get_user_with_asurite(asurite, 
                                         create=WEBAUTH_AUTOCREATE_USERS)
        except asuwebauth.NotAuthenticatedError as e:
            pass
        except Exception as e:
            LOG.error("Exception thrown authenticating, %s" % e)
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_with_asurite(asurite, create=False):
        '''
        Retrieve a local user object corresponding to the given ASURITE.  
        '''
        try:
            return User.objects.get(username=asurite)
        except User.DoesNotExist:
            if not create:
                return None
            return User.objects.create(username=asurite)
