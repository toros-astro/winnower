from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update$', views.update, name='update'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^circular$', views.circular, name='circular'),
    url(r'^login$', views.user_login, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
]