from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    model = User
    search_field = ('email', 'username', 'first_name', 'last_name', 'referer')
    list_filter = ('email', 'username', 'first_name', 'referer', 'wallet_address',
                   'last_name', 'is_active', 'is_staff')
    ordering = ('-date_joined',)
    list_display = ('username', 'id', 'email', 'first_name',
                    'last_name', 'referer', 'wallet_address', 'is_active', 'is_staff', 'last_login', 'date_joined')


admin.site.register(User, UserAdmin)
