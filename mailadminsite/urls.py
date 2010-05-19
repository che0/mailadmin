# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

adminurls = patterns('',
    (r'^password/$', 'mailadmin.views.change_mailbox_password'),
    (r'^password/changed/$', 'mailadmin.views.change_mailbox_password_ok'),
    (r'^mailadmin/mydomains/$', 'mailadmin.views.my_domains'),
    (r'', include(admin.site.urls)),
)

urlpatterns = patterns('',
    (settings.BASE_URL, include(adminurls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
