"""
URL configuration for cloudysky project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    # ↪︎ leave the built-in auth under /accounts/
    path('', include('app.urls')),      # root-level for human-facing pages
    path('app/', include('app.urls')),  # /app/ for API endpoints
    
    # Direct API endpoints (no app/ prefix) for absolute paths in tests
    path('createPost/', app_views.create_post),
    path('createPost', app_views.create_post),
    path('createComment/', app_views.create_comment),
    path('createComment', app_views.create_comment),
    path('hidePost/', app_views.hide_post),
    path('hideComment/', app_views.hide_comment),
    path('dumpFeed/', app_views.dump_feed),
    path('dumpUploads/', app_views.dump_uploads),
]