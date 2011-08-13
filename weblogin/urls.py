from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('weblogin.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
)
