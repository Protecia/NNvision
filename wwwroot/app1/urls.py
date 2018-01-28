from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^camera/$', views.camera, name='camera'),
	url(r'^settings/$', views.configuration, name='configuration'),
	url(r'^settings/wifi_add/$', views.wifi_add, name='wifi_add'),
	url(r'^settings/wifi_suppr/$', views.wifi_suppr, name='wifi_suppr'),
	url(r'^settings/wifi_restart/$', views.wifi_restart, name='wifi_restart'),
	url(r'^reboot/', views.reboot, name='reboot'),
	url(r'^shutdown/', views.shutdown, name='shutdown'),
]