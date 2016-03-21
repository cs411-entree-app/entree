from django.shortcuts import render

# Global site context
context_dict = {
    'version': 'v0.1'
}


def index(request):
    return render(request, 'entree/index.html', context_dict)


def about(request):
    return render(request, 'entree/about.html', context_dict)


def posts(request):

    if request.method == 'POST':
        city = request.POST['city']
        context_dict['city'] = city
    else:
        print('Cannot GET this page')

    return render(request, 'entree/posts.html', context_dict)

