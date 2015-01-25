from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^auth/', include('auth.urls', namespace="auth")),
    url(r'^admin/', include(admin.site.urls)),
)