from django.shortcuts import render

# Global site context
context_dict = {
    'version': '0.0.1'
}


def index(request):
    return render(request, 'entree/index.html', context_dict)
