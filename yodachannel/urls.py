from django.urls import path

from yodachannel import views

urlpatterns = [
    path('index', views.index_action, name='index'),
    path('profile', views.profile_action, name='profile'),
    path('mail/<str:order>', views.mail_action, name='mail'),
    path('mail_page', views.mail_page_action, name='mail_page'),
]
