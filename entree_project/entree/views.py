from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from entree.models import *
from entree.forms import RegisterForm, EditUserForm
from entree_project.settings import APP_VERSION, NUM_RESULTS
from datetime import timedelta
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import requests
import simplejson
import html.parser


FLICKR_REST_ROOT_URL = 'https://api.flickr.com/services/rest/?method='


# Global site context
context_dict = {
    'version': 'v' + APP_VERSION
}

def bad_request(request):
    context_dict['status_code'] = 400
    context_dict['status_name'] = 'Bad Request'
    context_dict['status_description'] = "Sorry, your request could not be understood by the server."
    response = render(request, 'error.html', context_dict)
    response.status_code = 400
    return response


def permission_denied(request):
    context_dict['status_code'] = 403
    context_dict['status_name'] = 'Permission Denied'
    context_dict['status_description'] = "Sorry, you do not have permission to access this page."
    response = render(request, 'error.html', context_dict)
    response.status_code = 403
    return response


def page_not_found(request):
    context_dict['status_code'] = 404
    context_dict['status_name'] = 'Page Not Found'
    context_dict['status_description'] = "Sorry, the page you were trying to view does not exist."
    response = render(request, 'error.html', context_dict)
    response.status_code = 404
    return response


def server_error(request):
    context_dict['status_code'] = 500
    context_dict['status_name'] = 'Server Error'
    context_dict['status_description'] = "Sorry, an error occured while processing your request."
    response = render(request, 'error.html', context_dict)
    response.status_code = 500
    return response


def login(request):

    login_failed = False
    new_login = True

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                login_failed = False
                return redirect('/entree/', context_dict)

        login_failed = True
        new_login = False

    else:

        # user redirected from registration page
        if 'registered' in request.GET:
            new_login = False

    context_dict['login_failed'] = login_failed
    context_dict['new_login'] = new_login
    return render(request, 'entree/login.html', context_dict)


@login_required
def logout(request):
    auth_logout(request)
    return redirect('/entree/login/', context_dict)


def register(request):

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():
            data = register_form.cleaned_data

            user = User(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email']
            )
            user.set_password(data['password'])
            user.save()

            profile = UserProfile(
                user=user
            )
            profile.save()

            context_dict['new_login'] = False
            return redirect('/entree/login/?registered=true', context_dict)

    else:
        register_form = RegisterForm()

    context_dict['register_form'] = register_form
    return render(request, 'entree/register.html', context_dict)


def about(request):
    return render(request, 'entree/about.html', context_dict)


@login_required
def profile(request):

    user = request.user

    if request.method == 'POST':
        user_form = EditUserForm(request.POST)

        if user_form.is_valid():
            data = user_form.cleaned_data

            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.save()

            return redirect('/entree/user/profile/', context_dict)
    else:

        if 'edit' in request.GET:
            editing = True

            user_form = EditUserForm(
                initial={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }
            )

        else:
            editing = False
            user_form = None

    context_dict['editing'] = editing
    context_dict['user_form'] = user_form
    return render(request, 'entree/profile.html', context_dict)


@login_required
def index(request):
    if 'invalid_search' in request.GET:
        context_dict['search_error'] = True
    else:
        context_dict['search_error'] = False
    return render(request, 'entree/index.html', context_dict)


@login_required
def posts(request):

    if 'city' not in request.GET:
        return redirect('/entree/' + '?invalid_search=true', context_dict)

    city = request.GET['city'].lower()

    if city == '':
        return redirect('/entree/' + '?invalid_search=true', context_dict)

    if 'page' in request.GET:
        page = int(request.GET['page'])

        if not page >= 1:
            page = 1
    else:
        page = 1  # start at the first page

    context_dict['city'] = city.title()
    context_dict['next_page'] = page + 1

    posts = __search_flickr_posts(city, page)

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
                search_term=city,
                page=page
            )
            flickrpost.save()

    context_dict['post_list'] = FlickrPost.objects.filter(search_term=city).filter(page=page).order_by('-date_fetched')
    return render(request, 'entree/posts.html', context_dict)


@login_required
def post_detail(request, photo_id):
    try:
        # get Flickr Post details
        post = FlickrPost.objects.get(pk=photo_id)
        context_dict['valid_post'] = True

        h = html.parser.HTMLParser()

        if not post.latitude or not post.longitude:
            photo = __get_flickr_post_info(photo_id)
            post.latitude = float(photo['location']['latitude'])
            post.longitude = float(photo['location']['longitude'])
            post.description = h.unescape(photo['description']['_content'])
            post.save()

        context_dict['post'] = post

        # get Yelp reviews for that location
        yelp = YelpClient.objects.get(pk=1)
        auth = Oauth1Authenticator(
            consumer_key=yelp.consumer_key,
            consumer_secret=yelp.consumer_secret,
            token=yelp.token,
            token_secret=yelp.token_secret
        )
        client = Client(auth)

        # get location that most closely matches the geolocation
        best_business = None
        alt_businesses = list()
        yelp_api_error = False

        try:
            response = client.search_by_coordinates(post.latitude, post.longitude)

            if response.businesses:
                best_business = response.businesses[0]

                if len(response.businesses) > 5:
                    alt_businesses = response.businesses[1:6]

                elif len(response.businesses) > 1:
                    alt_businesses = response.businesses[1:]

        except:
            yelp_api_error = True

        context_dict['yelp_api_error'] = yelp_api_error
        context_dict['best_business'] = best_business
        context_dict['alt_businesses'] = alt_businesses

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


def __search_flickr_posts(city, page):
    method = 'flickr.photos.search'
    params = {
        'tags': city + ',food',
        'tag_mode': 'all',              # only return photos that include all of the tags
        'privacy_filter': 1,            # 1 = public
        'has_geo': 1,                   # only return images that have geolocation information
        'per_page': NUM_RESULTS,
        'page': page
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

