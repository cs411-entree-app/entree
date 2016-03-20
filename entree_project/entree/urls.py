from django.conf.urls import url
from entree import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]