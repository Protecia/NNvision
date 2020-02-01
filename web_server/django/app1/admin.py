
from django.contrib import admin
from django.conf import settings
from django.forms.models import ModelForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy as _

# Register your models here.

from .models import Client, Camera, Result, Object, Profile, Alert, Alert_when, Alert_type, Telegram, Update_id


@receiver(post_save, sender= User)
def add_group_permission(sender, instance, created, **kwargs):
    if created:
        g = Group.objects.get(name='normal')
        g.user_set.add(instance)

class CameraAdmin(admin.ModelAdmin):
    exclude = ('wait_for_set','update','from_client')
    '''
    def delete_model(self, request, obj):
        client = Profile.objects.get(user=request.user).client
        client.camera = 1
        client.save()
    '''

    def get_readonly_fields(self, request, obj=None):
        fields=self.readonly_fields
        if obj and obj.from_client == True :
            fields += ('ip','port_onvif','url','auth_type','rtsp','brand','client','model')
        if not request.user.is_superuser :
            fields += ('threshold','gap','pos_sensivity','reso','width','height', 'max_width_rtime')
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

class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ('key','folder',)
    


admin.site.register(Camera, CameraAdmin)


if settings.DEBUG:
    admin.site.register(Result)
    admin.site.register(Object)
    admin.site.register(Alert)
    admin.site.register(Alert_when)
    admin.site.register(Alert_type)
    admin.site.register(Client, ClientAdmin)
    admin.site.register(Telegram)
    





from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class AlwaysChangedModelForm(ModelForm):
    def has_changed(self, *args, **kwargs):
        if self.instance.pk is None:
            return True
        return super(AlwaysChangedModelForm, self).has_changed(*args, **kwargs)

class ProfileInline(admin.StackedInline):
    model = Profile
    form = AlwaysChangedModelForm
    can_delete = False
    #filter_horizontal = ['phone_number',]  # example: ['tlf', 'country',...]
    verbose_name_plural = 'profiles'
    fk_name = 'user'
    def get_readonly_fields(self, request, obj=None):
        fields=self.readonly_fields
        if not request.user.is_superuser :
            fields += ('client','telegram_token',)
        return fields

class MyUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if request.user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
        else:
            # modify these to suit the fields you want your
            # staff user to be able to edit
            perm_fields = ('is_active',)

        return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': perm_fields}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')})]
    
    def get_readonly_fields(self, request, obj=None):
        fields=self.readonly_fields
        if not request.user.is_superuser :
            fields += ('last_login','date_joined',)
        return fields
    
    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(profile__client=Profile.objects.get(user=request.user).client)
    
    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            obj.save()
        else :
            if getattr(obj, 'client', None) is None:
                obj.client = Profile.objects.get(user=request.user).client
            obj.save()

    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_active')

admin.site.unregister(User)  # Unregister user to add new inline ProfileInline
admin.site.register(User, MyUserAdmin)  # Register User with this inline profile
