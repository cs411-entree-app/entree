"""entree_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from entree import views

handler400 = 'entree.views.bad_request'
handler403 = 'entree.views.permission_denied'
handler404 = 'entree.views.page_not_found'
handler500 = 'entree.views.server_error'

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='entree/')),
    url(r'^entree/', include('entree.urls', namespace='entree')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^400/$', views.bad_request),
        url(r'^403/$', views.permission_denied),
        url(r'^404/$', views.page_not_found),
        url(r'^500/$', views.server_error),
    ]
