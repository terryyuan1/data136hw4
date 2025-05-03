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
]
