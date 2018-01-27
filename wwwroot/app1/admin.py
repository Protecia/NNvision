from django.contrib import admin

# Register your models here.

from .models import Cameras, Results

admin.site.register(Cameras)
admin.site.register(Results)
