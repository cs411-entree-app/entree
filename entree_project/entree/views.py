from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

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
                # redirect to homepage
                return redirect('/entree/', context_dict)

            return render(request, 'entree/login.html', context_dict)
        return render(request, 'entree/login.html', context_dict)

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
        city = request.POST['city']
        context_dict['city'] = city
    else:
        print('Cannot GET this page')

    return render(request, 'entree/posts.html', context_dict)

