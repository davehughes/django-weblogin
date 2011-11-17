Django Weblogin
===============
Django auth backend for connecting to the Arizona State University single sign-on systems ([webauth/weblogin](http://asu.edu/webauth/implement.htm)).  This
module was developed as a component of the [ASU Digital Repository](http://repository.asu.edu).

[foo](davehughes/webauth)

###Installation:
####Install packages:
```
pip install -e git://github.com/davehughes/webauth.git#egg=webauth
pip install -e git://github.com/davehughes/django-weblogin.git#egg=webauth
```

####Add URL routes to login/logout:
```python
# In urls.py
...

urlpatterns += ('weblogin.views',
  url('^login/$', 'login', name='login'),
  url('^logout/$', 'logout', name='logout'),
  )
  
...

```

####Add the auth handler and webauth/weblogin settings:
```python
# In settings.py
AUTHENTICATION_BACKENDS = (
  'weblogin.WebLoginBackend',  # or substitute your custom subclass (see below)
  ...
)

...

# Default settings: these are optional, but should be specified if your configuration differs
WEBAUTH_HOST = 'webauth.asu.edu'
WEBAUTH_PORT = 3001
WEBAUTH_TOKEN_COOKIE = 'ASUWEBAUTH'

WEBLOGIN_HOST = 'https://weblogin.asu.edu/cgi-bin/cas-login'
```

####Optional: Customize the auth handler
This is not strictly necessary, but is useful for controlling how users are created.  We use a custom subclass that
queries an internal service based on the user's single sign-on ID and adds useful information (first and last names, 
email addresses) to the user record.

The (mostly useless) snippet below creates every user a superuser and gives each one the name "Joe Foo" and the email 
address "foo@example.com".

```python
from django.contrib.auth.models import User
import weblogin

class CustomAuthBackend(weblogin.WebLoginBackend):

  def get_user_with_asurite(self, asurite):
    user_defaults = {'first_name': 'Joe', 'last_name': 'Foo', 'email': 'foo@example.com'}
    user, _ = User.objects.get_or_create(username=asurite, defaults=user_defaults)
    user.is_superuser = True
    user.save()
    return user
```

###Caveats:
+ **The login loop will cause infinite redirects if the host it's running on is not in the *.asu.edu domain.** 
  This is because weblogin sets an auth cookie in this domain that is needed for webauth to verify a user's authentication. 
  If the host can't see this cookie, it thinks it's seeing a new login request, and will redirect to weblogin ad 
  infinitum.