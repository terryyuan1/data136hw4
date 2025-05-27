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
    path('app/createUser/', views.create_user),  # with app prefix
    path('app/createUser', views.create_user),  # with app prefix, without trailing slash
    
    # createPost endpoint
    path('createPost/', views.create_post, name='create_post'),
    path('createPost', views.create_post),  # without trailing slash
    path('app/createPost/', views.create_post),  # with app prefix
    path('app/createPost', views.create_post),  # with app prefix, without trailing slash
    
    # createComment endpoint
    path('createComment/', views.create_comment, name='create_comment'),
    path('createComment', views.create_comment),  # without trailing slash
    path('app/createComment/', views.create_comment),  # with app prefix
    path('app/createComment', views.create_comment),  # with app prefix, without trailing slash
    
    # hidePost endpoint
    path('hidePost/', views.hide_post, name='hide_post'),
    path('hidePost', views.hide_post),  # without trailing slash
    path('app/hidePost/', views.hide_post),  # with app prefix
    path('app/hidePost', views.hide_post),  # with app prefix, without trailing slash
    
    # hideComment endpoint
    path('hideComment/', views.hide_comment, name='hide_comment'),
    path('hideComment', views.hide_comment),  # without trailing slash
    path('app/hideComment/', views.hide_comment),  # with app prefix
    path('app/hideComment', views.hide_comment),  # with app prefix, without trailing slash
    
    # dumpFeed endpoint
    path('dumpFeed/', views.dump_feed, name='dump_feed'),
    path('dumpFeed', views.dump_feed),  # without trailing slash
    path('app/dumpFeed/', views.dump_feed),  # with app prefix
    path('app/dumpFeed', views.dump_feed),  # with app prefix, without trailing slash
    
    # dumpUploads endpoint
    path('dumpUploads/', views.dump_uploads, name='dump_uploads'),
    path('dumpUploads', views.dump_uploads),  # without trailing slash
    path('app/dumpUploads/', views.dump_uploads),  # with app prefix
    path('app/dumpUploads', views.dump_uploads),  # with app prefix, without trailing slash
    
    # New endpoints for HW6
    # app/feed endpoint
    path('app/feed/', views.app_feed, name='app_feed'),
    path('app/feed', views.app_feed),  # without trailing slash
    
    # app/post/<post_id> endpoint
    path('app/post/<int:post_id>/', views.app_post_detail, name='app_post_detail'),
    path('app/post/<int:post_id>', views.app_post_detail),  # without trailing slash
]

if __name__ == "__main__":
    unittest.main()
