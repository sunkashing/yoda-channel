from django.urls import path

from yodachannel import views

urlpatterns = [
    path('index', views.index_action, name='index'),
    path('profile', views.profile_action, name='profile'),

]