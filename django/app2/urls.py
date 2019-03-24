from django.urls import path

from . import views
from app2.admin import admin_site

urlpatterns = [
    path('', views.index, name='index'),
    path('insert', views.insert_img, name='insert'),
    path('admin/', admin_site.urls)
]