from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from entree.models import *
from datetime import timedelta
import requests
import simplejson

FLICKR_REST_ROOT_URL = 'https://api.flickr.com/services/rest/?method='


# Global site context
context_dict = {
    'version': 'v1.0'
}


def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('/entree/', context_dict)

    return render(request, 'entree/login.html', context_dict)


@login_required
def logout(request):
    auth_logout(request)
    return render(request, 'entree/login.html', context_dict)


def about(request):
    return render(request, 'entree/about.html', context_dict)


@login_required
def index(request):
    return render(request, 'entree/index.html', context_dict)


@login_required
def posts(request):

    if request.method == 'POST':
        city = request.POST['city'].lower()
        # return the search items as debug info for now
        context_dict['city'] = city.title()

        # check if latest cached post was recent (within last day)
        try:
            latest_post = FlickrPost.objects.filter(search_term=city).latest('date_fetched')

            if latest_post:
                now = timezone.now()
                then = now - timedelta(days=1)
                if latest_post.date_fetched < then:
                    # cache is expired, update with any new posts
                    posts = __search_flickr_posts(city)

                    for post in posts:
                        if not FlickrPost.objects.filter(id=post['id']).count():
                            # post not already in database
                            flickrpost = FlickrPost(
                                id=post['id'],
                                secret=post['secret'],
                                farm=post['farm'],
                                server=post['server'],
                                owner=post['owner'],
                                title=post['title'],
                                image_url=post['url'],
                                search_term=city
                            )
                            flickrpost.save()

                else:
                    # cache is up-to-date
                    post_list = FlickrPost.objects.filter(search_term=city).order_by('date_fetched')
                    context_dict['post_list'] = post_list

        except FlickrPost.DoesNotExist:
            # there are no records in the database for this search term yet
            posts = __search_flickr_posts(city)
            post_list = list()

            for post in posts:

                # add post to database
                flickrpost = FlickrPost(
                    id=post['id'],
                    secret=post['secret'],
                    farm=post['farm'],
                    server=post['server'],
                    owner=post['owner'],
                    title=post['title'],
                    image_url=post['url'],
                    search_term=city
                )
                flickrpost.save()
                post_list.append(flickrpost)

            context_dict['post_list'] = post_list
    else:
        return redirect('/entree/', context_dict)

    return render(request, 'entree/posts.html', context_dict)


@login_required
def post_detail(request, photo_id):
    try:
        post = FlickrPost.objects.get(pk=photo_id)
        context_dict['valid_post'] = True

        if not post.latitude or not post.longitude:
            photo = __get_flickr_post_info(photo_id)
            post.latitude = float(photo['location']['latitude'])
            post.longitude = float(photo['location']['longitude'])
            post.description = photo['description']['_content']
            post.save()

        context_dict['post'] = post

    except FlickrPost.DoesNotExist:
        context_dict['valid_post'] = False

    return render(request, 'entree/post_detail.html', context_dict)


def __get_flickr_post_info(photo_id):
    method = 'flickr.photos.getInfo'
    params = {
        'photo_id': photo_id
    }
    url = __build_flickr_rest_url(method, params)

    response = simplejson.loads(__flickr_json_fix(requests.get(url).text))
    return response['photo']


def __search_flickr_posts(city):
    method = 'flickr.photos.search'
    params = {
        'tags': city + ',food',
        'tag_mode': 'all',              # only return photos that include all of the tags
        'privacy_filter': 1,            # 1 = public
        'has_geo': 1,                   # only return images that have geolocation information
        'per_page': 25
    }
    url = __build_flickr_rest_url(method, params)

    response = simplejson.loads(__flickr_json_fix(requests.get(url).text))
    photos = response['photos']['photo']
    image_url = 'https://farm{0}.staticflickr.com/{1}/{2}_{3}.jpg'
    post_list = list()

    for i in range(len(photos)):
        post = photos[i]
        post['url'] = image_url.format(post['farm'], post['server'], post['id'], post['secret'])
        post_list.append(post)

    return post_list


def __build_flickr_rest_url(method, params):
    flickr = FlickrClient.objects.get(pk=1)
    url = FLICKR_REST_ROOT_URL
    url += method
    params['api_key'] = flickr.api_key
    params['format'] = 'json'

    for key in params.keys():
        url += '&' + str(key) + '=' + str(params[key])

    return url


def __flickr_json_fix(json_string):
    # Removes the "jsonFlickrApi( ... )" wrapper around the response's JSON
    return json_string.replace('jsonFlickrApi(', '').replace(')', '')

