from django.contrib import admin

# Register your models here.

from .models import Camera, Result, Info, Object, Profile, Alert

admin.site.register(Camera)
admin.site.register(Result)
admin.site.register(Info)
admin.site.register(Object)
admin.site.register(Profile)
admin.site.register(Alert)


from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    #filter_horizontal = ['phone_number',]  # example: ['tlf', 'country',...]
    verbose_name_plural = 'profiles'
    fk_name = 'user'

class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

admin.site.unregister(User)  # Unregister user to add new inline ProfileInline
admin.site.register(User, UserAdmin)  # Register User with this inline profile
