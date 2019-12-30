from django.contrib import admin
from django.conf import settings

# Register your models here.

from .models import Client, Camera, Result, Object, Profile, Alert, Alert_when, Alert_type, Alert_adam, Alert_hook

class CameraAdmin(admin.ModelAdmin):
    exclude = ('wait_for_set','update','from_client')
    '''
    def delete_model(self, request, obj):
        client = Profile.objects.get(user=request.user).client
        client.camera = 1
        client.save()
        super().delete_model(request, obj)
    '''
        
    def get_readonly_fields(self, request, obj=None):
        fields=self.readonly_fields
        if obj and obj.from_client == True :
            fields += ('ip','port_onvif','url','auth_type','rtsp','brand','client','model')
        if not request.user.is_superuser :
            fields += ('threshold','gap','pos_sensivity','reso','width','height')
        return fields
    
    
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'client', None) is None:
            obj.client = Profile.objects.get(user=request.user).client
            obj.update=1
        obj.save()
    def get_queryset(self, request):
        qs = super(CameraAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=Profile.objects.get(user=request.user).client)
    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        return request.user.is_superuser or obj.client == Profile.objects.get(user=request.user).client
    
    def get_exclude(self, request, obj=None):
        excluded = super().get_exclude(request, obj) or [] # get overall excluded fields

        if not request.user.is_superuser: # if user is not a superuser
            return excluded + ('client',)

        return excluded # otherwise return the default excluded fields if any


admin.site.register(Camera, CameraAdmin)
admin.site.register(Profile)
admin.site.register(Alert_type)
admin.site.register(Client)
if settings.ACCESS_ADAM:
    admin.site.register(Alert_adam)
if settings.ACCESS_HOOK:
    admin.site.register(Alert_hook)

if settings.DEBUG:
    admin.site.register(Result)
    admin.site.register(Object)
    admin.site.register(Alert)
    admin.site.register(Alert_when)




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
