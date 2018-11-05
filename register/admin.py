from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import MyGroup, User, Workspace


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', )


class MyGroupAdmin(admin.ModelAdmin):
    pass


class WorkspaceAdmin(admin.ModelAdmin):
    pass


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'workspace',
                       'is_workspace_active', 'workspace_role', 'my_group')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('email', 'password1', 'password2'),
    }), )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', )


admin.site.register(User, MyUserAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(MyGroup, MyGroupAdmin)
