from django.urls import path

from yodachannel import views

urlpatterns = [
    path('index', views.index_action, name='index'),
    path('profile', views.profile_action, name='profile'),
    path('mail/<str:order>', views.mail_action, name='mail'),
    path('mail_page', views.mail_page_action, name='mail_page'),
    path('blog/<str:order>', views.blog_action, name='blog'),
    path('blog_page', views.blog_page_action, name='blog_page'),
    path('blog_view/<int:blog_id>', views.blog_view_action, name='blog_view'),
    path('video/<str:order>', views.video_action, name='video'),
    path('video_view/<str:path>', views.get_video_action, name='video_view'),

]
