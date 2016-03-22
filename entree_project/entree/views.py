from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from entree.models import *
import requests

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

                # check if user has Instagram auth_token already
                profile = UserProfile.objects.get(user=user)

                if profile.instagram_auth_token:
                    # redirect to homepage
                    return redirect('/entree/', context_dict)

                else:
                    # authenticate with Instagram to obtain auth_token
                    instagram = InstagramClient.objects.get(pk=1)
                    client_id = instagram.client_id
                    redirect_uri = instagram.redirect_uri
                    uri = 'https://api.instagram.com/oauth/authorize/?response_type=code'
                    uri += '&client_id=' + requests.utils.quote(client_id, safe='')
                    uri += '&redirect_uri=' + requests.utils.quote(redirect_uri, safe='')
                    return redirect(uri, context_dict)

            return render(request, 'entree/login.html', context_dict)
        return render(request, 'entree/login.html', context_dict)

    return render(request, 'entree/login.html', context_dict)


@login_required
def insta_auth(request):
    # request format:
    # http://entree.noip.me/insta/auth/?code=586e03f5daa841119ced64e0ff971b90
    code = request.GET['code']
    instagram = InstagramClient.objects.get(pk=1)
    uri = 'https://api.instagram.com/oauth/access_token'
    post_data = {
        'client_id': instagram.client_id,
        'client_secret': instagram.client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': instagram.redirect_uri,
        'code': code,
    }
    response = request.post(uri, data=post_data)
    data = response.json()  # convert response body to json object
    access_token = data['access_token']

    # add access token to user profile
    profile = UserProfile.objects.get(user=request.user)
    profile.instagram_auth_token = access_token
    profile.save()

    return redirect('/entree/', context_dict)


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
        city = request.POST['city']
        context_dict['city'] = city
    else:
        print('Cannot GET this page')

    return render(request, 'entree/posts.html', context_dict)

