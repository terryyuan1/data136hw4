# cloudysky/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app.views import index

urlpatterns = [
    # home page (both “/” and “/index.html”)
    path('',           index, name='root_index'),
    path('index.html', index, name='index_html'),

    # admin site
    path('admin/', admin.site.urls),

    # your app’s URLs (/app/...)
    path('app/', include('app.urls')),

    # login/logout
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        # you can omit name here since you only need {% url 'login' %} for the one above
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'
    ),
]
