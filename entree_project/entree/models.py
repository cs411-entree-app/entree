from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    # default User includes:
    # username
    # first_name
    # last_name
    # email
    # password
    # groups
    # is_staff
    # is_active
    # is_superuser
    # last_login
    # date_joined

    # links to Django User implementation
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=False
    )
    instagram_auth_token = models.CharField(
        max_length=255,
        blank=True
    )
    search_radius = models.PositiveSmallIntegerField(
        blank=False
    )
    '''
    # omit these for now
    current_city = models.ForeignKey(
        City,
        blank=False
    )
    lat = models.DecimalField(
        default=0,
        decimal_places=6,
        max_digits=9,
        blank=False
    )
    long = models.DecimalField(
        default=0,
        decimal_places=6,
        max_digits=9,
        blank=False
    )
    '''


class InstagramClient(models.Model):

    # stores Entree's Instagram API access information securely

    client_id = models.CharField(
        max_length=32,
        blank=False
    )
    client_secret = models.CharField(
        max_length=32,
        blank=False
    )
    redirect_uri = models.CharField(
        max_length=255,
        blank=False
    )
