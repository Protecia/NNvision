from django import VERSION as v
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from . import views

if v[0] >=2 : 
    from django.urls import path, include
    urlpatterns = [
        path('accounts/', include('django.contrib.auth.urls')),
        url(r'^$', views.index, name='index'),
        url(r'^camera/$', views.camera, name='camera'),
        url(r'^darknet/$', views.darknet, name='darknet'),
        url(r'^darknet/state/$', views.darknet_state, name='ds'),
        path('panel/<int:first>', views.panel, name='panel'),
        path('alert', views.alert, name='alert'),
        url(r'^panel/detail/(?P<id>\d+)$', views.panel_detail, name='detail'),
        url(r'^settings/$', views.configuration, name='configuration'),
        url(r'^settings/wifi_add/$', views.wifi_add, name='wifi_add'),
        url(r'^settings/wifi_suppr/$', views.wifi_suppr, name='wifi_suppr'),
        url(r'^settings/wifi_restart/$', views.wifi_restart, name='wifi_restart'),
        url(r'^reboot/', views.reboot, name='reboot'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
else :
    from django.conf.urls import include
    urlpatterns = [
        url(r'^accounts/', include('django.contrib.auth.urls')),
        url(r'^$', views.index, name='index'),
        url(r'^camera/$', views.camera, name='camera'),
        url(r'^darknet/$', views.darknet, name='darknet'),
        url(r'^darknet/state/$', views.darknet_state, name='ds'),
        url(r'^panel/(?P<first>\d+)$', views.panel, name='panel'),
        url(r'^alert/$', views.alert, name='alert'),
        url(r'^panel/detail/(?P<id>\d+)$', views.panel_detail, name='detail'),
        url(r'^settings/$', views.configuration, name='configuration'),
        url(r'^settings/wifi_add/$', views.wifi_add, name='wifi_add'),
        url(r'^settings/wifi_suppr/$', views.wifi_suppr, name='wifi_suppr'),
        url(r'^settings/wifi_restart/$', views.wifi_restart, name='wifi_restart'),
        url(r'^reboot/', views.reboot, name='reboot'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    