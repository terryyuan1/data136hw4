# app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Human‐facing pages (index, signup form, new‐post/comment forms, login) —
    path('',             views.index,     name='index_html'),  # still serve "/" for convenience
    path('index.html',   views.index,     name='index'),
    path('new/',         views.new_user,  name='new_user'),
    path('new_post/',    views.new_post,  name='new_post'),
    path('new_comment/', views.new_comment, name='new_comment'),
    path('login/',       auth_views.LoginView.as_view(
                            template_name='registration/login.html'),
                        name='login'),

    # API endpoints with variations to handle different URL patterns
    # createUser endpoint
    path('createUser/', views.create_user, name='create_user'),
    path('createUser', views.create_user),  # without trailing slash
    
    # createPost endpoint
    path('createPost/', views.create_post, name='create_post'),
    path('createPost', views.create_post),  # without trailing slash
    
    # createComment endpoint
    path('createComment/', views.create_comment, name='create_comment'),
    path('createComment', views.create_comment),  # without trailing slash
    
    # hidePost endpoint
    path('hidePost/', views.hide_post, name='hide_post'),
    path('hidePost', views.hide_post),  # without trailing slash
    
    # hideComment endpoint
    path('hideComment/', views.hide_comment, name='hide_comment'),
    path('hideComment', views.hide_comment),  # without trailing slash
    
    # dumpFeed endpoint
    path('dumpFeed/', views.dump_feed, name='dump_feed'),
    path('dumpFeed', views.dump_feed),  # without trailing slash
    
    # dumpUploads endpoint
    path('dumpUploads/', views.dump_uploads, name='dump_uploads'),
    path('dumpUploads', views.dump_uploads),  # without trailing slash
]

if __name__ == "__main__":
    unittest.main()
