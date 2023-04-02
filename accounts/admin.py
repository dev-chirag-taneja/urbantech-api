from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active', 'is_staff')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    add_fieldsets = (
            (None, {'fields': ('first_name', 'last_name', 'email', 'password1', 'password2', 'is_admin', 'is_active', 'is_staff')}),
        )


admin.site.register(User, UserAdmin)
admin.site.register(Profile)