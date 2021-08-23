"""facepage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
#from posts.views import getProfilePosts
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts.views import profile


urlpatterns = [
    path(r'admin/', admin.site.urls, name='admin'),
    path(r'', include('users.urls'), name='users'),
    path(r'home/', include('posts.urls'), name='home'),
    path(r'profile/<slug:link>/', profile, name='profile'),
    #path(r'profile/<slug:link>/get/', getProfilePosts, name='profile-posts'),
    path(r'messenger/', include('messenger.urls'), name='messenger'),
    path(r'notifications/', include('notifications.urls'), name='notifications'),
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

