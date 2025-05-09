from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home
    path('',            views.index,      name='index'),
    path('index.html',  views.index,      name='index'),

    # Sign-up form
    path('new/',        views.new_user,   name='new_user'),

    # Create user (POST only; grader hits /createUser)
    path('createUser',  views.create_user, name='create_user'),

    # Login (GET+POST)
    path('login/', auth_views.LoginView.as_view(
         template_name='registration/login.html'), name='login'),
    # Form‐view endpoints
    path('new_post',    views.new_post,    name='new_post'),
    path('new_comment', views.new_comment, name='new_comment'),

    # API endpoints
    path('createPost',    views.create_post,    name='create_post'),
    path('createComment', views.create_comment, name='create_comment'),
    path('hidePost',      views.hide_post,      name='hide_post'),
    path('hideComment',   views.hide_comment,   name='hide_comment'),
    path('dumpFeed',      views.dump_feed,      name='dump_feed'),
]

