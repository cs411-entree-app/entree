from django.conf.urls import url
from entree import views

app_name = 'entree'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'posts/', views.posts, name='posts'),
]