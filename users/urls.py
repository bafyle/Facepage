from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path(r'', index, name='index'),
    path(r'logout/', logoutFunction, name='logout'),
    path(r'login/', loginFunction, name='login'),
    path(r'register/', register, name='register'),
    path(r'settings/', accountSettings, name='settings'),
    path(r'delete-account/', deleteAccount, name='delete'),
    path(r'changebio/', changeBioAndProfilePicture, name='change-bio'),
    path(r'delete-profile-picture/', deleteMyProfilePicture, name='delete-profile-picture'),
    path(r'verification/', verifyEmailView, name='verification-sent'),
    path(r'activate/<uidb64>/<token>/', activate, name='activate'),
    path(r'personalsettings/', personalSettings, name='personal-settings'),

    
]
