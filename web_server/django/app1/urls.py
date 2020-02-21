from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.urls import path, include
from . import views, api

favicon_view = RedirectView.as_view(url='/static/app1/img/favicon.ico', permanent=True)

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^camera/$', views.camera, name='camera'),
    path('panel/<str:nav>/<int:first>', views.panel, name='panel'),
    path('warning/<int:first_alert>/<str:key>', views.warning, name='warning'),
    path('warning_detail/<int:id>/<str:key>', views.warning_detail, name='warning_detail'),
    path('alert/', views.alert, name='alert'),
    path('alert/<str:suppr>/<str:pk>', views.alert, name='alert'),
    path('panel_detail/<int:id>', views.panel_detail, name='detail'),
    path('camera/last/<int:cam>', views.last, name='last image'),
    path('img/last/<int:cam_id>', views.get_last_analyse_img, name='image'),
    path('thumbnail/<int:im>/<str:key>/<int:w>/<int:h>', views.thumbnail, name='thumbnail'),
    path('uploadimage', api.uploadImage),
    path('getCam', api.getCam),
    #path('getScheme', api.getScheme),
    path('uploadresult', api.uploadResult),
    path('setCam', api.setCam),
    path('getState', api.getState),
    path('upCam', api.upCam),
    path('favicon.ico', favicon_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
