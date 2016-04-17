from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from entree.models import UserProfile, FlickrClient, FlickrPost, YelpClient

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


class FlickrClientAdmin(admin.ModelAdmin):
    list_display = [
        'api_key',
        'secret_key',
    ]

admin.site.register(FlickrClient, FlickrClientAdmin)


class FlickrPostAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'search_term',
        'image_url',
        'latitude',
        'longitude',
        'date_fetched',
    ]
    search_fields = [
        'id',
    ]
    readonly_fields = [
        'id',
    ]

admin.site.register(FlickrPost, FlickrPostAdmin)


class YelpClientAdmin(admin.ModelAdmin):
    list_display = [
        'consumer_key',
        'consumer_secret',
        'token',
        'token_secret'
    ]

admin.site.register(YelpClient, YelpClientAdmin)
