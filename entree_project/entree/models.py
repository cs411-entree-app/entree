from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):

    """
    Extends the default Django User model. The default user includes:
    - username
    - first_name
    - last_name
    - email
    - password
    - groups
    - is_staff
    - is_active
    - is_superuser
    - last_login
    - date_joined
    """

    user = models.OneToOneField(
        User, # refers to Django User implementation
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


class FlickrClient(models.Model):

    """
    Stores our flickr API key securely on the server.
    """

    api_key = models.CharField(
        max_length=32,
        blank=False
    )
    secret_key = models.CharField(
        max_length=16,
        blank=False
    )


class FlickrPost(models.Model):

    """
    For caching flickr post information on the server between searches.

    All fields but 'latitude' and 'longitude' are populated when the post is first fetched from the server.
    The latitude and longitude fields are then populated by a separate API request the first time the post
    is viewed in detail. This dramatically improves the performance of the initial post list.
    """

    id = models.BigIntegerField(  # we use this for pk lookup of posts
        primary_key=True,
        blank=False
    )
    secret = models.CharField(
        max_length=32,
        blank=False
    )
    farm = models.PositiveSmallIntegerField(  # supports values up to 32767, maybe more (database dependent)
        blank=False
    )
    server = models.PositiveSmallIntegerField(
        blank=False
    )
    owner = models.CharField(
        max_length=32,
        blank=False
    )
    title = models.CharField(
        max_length=256,
        blank=True
    )
    image_url = models.CharField(  # we generate this during pre-processing on the server
        max_length=512,
        blank=False
    )
    search_term = models.CharField(  # the associated search term that was used to fetch this post
        max_length=64,
        blank=False
    )
    date_fetched = models.DateTimeField(
        default=timezone.now,
        blank=False
    )
    latitude = models.DecimalField(  # between -90 and 90 degrees
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(  # between -180 and 180 degrees
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    description = models.TextField(
        blank=True
    )


class YelpClient(models.Model):

    """
    Stores our Yelp API keys securely on the server.
    """
    consumer_key = models.CharField(
        max_length=32,
        blank=False
    )
    consumer_secret = models.CharField(
        max_length=32,
        blank=False
    )
    token = models.CharField(
        max_length=32,
        blank=False
    )
    token_secret = models.CharField(
        max_length=32,
        blank=False
    )
