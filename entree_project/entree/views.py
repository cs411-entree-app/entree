from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from entree.models import *
import requests
import simplejson

FLICKR_REST_ROOT_URL = 'https://api.flickr.com/services/rest/?method='


# Global site context
context_dict = {
    'version': 'v0.1'
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
        context_dict['search_items'] = "{0}, {1}".format(city, 'food')

        # check to see if there are results cached for this search term
        post_list = FlickrPost.objects.filter(search_term=city)

        if not post_list:
            print('NOT cached, fetching...')
            # no posts have been fetched for this term recently, go out to the API
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
                url = image_url.format(post['farm'], post['server'], post['id'], post['secret'])

                # add post to database
                flickrpost = FlickrPost(
                    id=post['id'],
                    secret=post['secret'],
                    farm=post['farm'],
                    server=post['server'],
                    owner=post['owner'],
                    title=post['title'],
                    image_url=url,
                    search_term=city
                )
                flickrpost.save()
                post_list.append(flickrpost)

        print('CACHED, querying database...')
        context_dict['post_list'] = post_list

    else:
        return redirect('/entree/', context_dict)

    return render(request, 'entree/posts.html', context_dict)


@login_required
def post_detail(request, photo_id):

    # get photo details
    context_dict['photo_id'] = photo_id

    return render(request, 'entree/post_detail.html', context_dict)


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

