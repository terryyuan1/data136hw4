# app/urls.py
from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

app_name = "app"

urlpatterns = [
    # -- Human-facing pages (index, signup form, new-post/comment forms, login) --
    path('',               views.index,     name='index'),
    path('index.html',     views.index,     name='index_html'),
    path('new/',           views.new_user,  name='new_user'),
    path('new_post/',      views.new_post,  name='new_post'),
    path('new_comment/',   views.new_comment,name='new_comment'),
    path('login/',         auth_views.LoginView.as_view(
                               template_name='registration/login.html'),
                               name='login'),

    # -- API endpoints, with optional trailing slash --
    re_path(r'^createUser/?$',
            views.create_user,
            name='create_user'),
    re_path(r'^createPost/?$',
            views.create_post,
            name='create_post'),
    re_path(r'^createComment/?$',
            views.create_comment,
            name='create_comment'),
    re_path(r'^hidePost/?$',
            views.hide_post,
            name='hide_post'),
    re_path(r'^hideComment/?$',
            views.hide_comment,
            name='hide_comment'),
    re_path(r'^dumpFeed/?$',
            views.dump_feed,
            name='dump_feed'),
]
