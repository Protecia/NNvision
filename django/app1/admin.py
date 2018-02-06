from django.contrib import admin

# Register your models here.

from .models import Camera, Result, Info, Object

admin.site.register(Camera)
admin.site.register(Result)
admin.site.register(Info)
admin.site.register(Object)
