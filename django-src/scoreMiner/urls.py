from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<uid>[0-9]+)/$', views.postList, name='posts')
]
