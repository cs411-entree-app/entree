from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from entree.models import UserProfile

# Add UserProfile inline with User
admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [
        UserProfileInline,
    ]
    readonly_fields = [
        'last_login',
        'date_joined',
    ]
    search_fields = [
        'username',
        'first_name',
        'last_name',
    ]

admin.site.register(User, UserProfileAdmin)
