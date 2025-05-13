# app/urls.py

from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Existing utility endpoints
    path("dummypage",        views.dummypage,      name="dummypage"),
    path("time",             views.get_time,      name="get_time"),
    path("sum",              views.get_sum,       name="get_sum"),

    # Index
    path("",                 views.index,         name="index"),

    # User signup
    path("new",              views.new_user_form),
    path("new/",             views.new_user_form, name="new_user"),
    path("createUser",       views.create_user),
    path("createUser/",      views.create_user,   name="create_user"),

    # New Post form & API
    path("new_post",         views.new_post),
    path("new_post/",        views.new_post,      name="new_post"),
    path("createPost",       views.create_post),
    path("createPost/",      views.create_post,   name="create_post"),

    # New Comment form & API
    path("new_comment",      views.new_comment),
    path("new_comment/",     views.new_comment,   name="new_comment"),
    path("createComment",    views.create_comment),
    path("createComment/",   views.create_comment,name="create_comment"),

    # Hide/Censor endpoints
    path("hidePost",         views.hide_post),
    path("hidePost/",        views.hide_post,     name="hide_post"),
    path("hideComment",      views.hide_comment),
    path("hideComment/",     views.hide_comment,  name="hide_comment"),

    # Dump feed (admin-only JSON dump)
    path("dumpFeed",         views.dump_feed),
    path("dumpFeed/",        views.dump_feed,     name="dump_feed"),
]