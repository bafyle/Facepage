from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path(r'', index, name='index'),
    path(r'logout/', logoutFunction, name='logout'),
    path(r'login/', loginFunction, name='login'),
    path(r'register/', register, name='register'),
    path(r'account-settings/', accountSettings2, name='account-settings'),
    path(r'delete-account/', deleteAccount, name='delete'),
    #path(r'changebio/', changeBioAndProfilePicture, name='change-bio'),
    path(r'delete-profile-picture/', deleteMyProfilePicture, name='delete-profile-picture'),
    path(r'delete-profile-cover/', deleteMyProfileCover, name='delete-profile-cover'),
    path(r'activate/<uidb64>/<token>/', activate, name='activate'),
    path(r'personal-settings/', personalSettings, name='personal-settings'),
    path(r'send-friend-request/<slug:link>/', sendFriendRequest, name='add-friend'),
    path(r'accept-friend-request/<slug:link>/', acceptFriendRequest, name='create-friend'),
    path(r'decline-friend-request/<slug:link>/', declineFriendRequest, name='decline-friend'),
    path(r'unfriend/<slug:link>/', unfriend, name='unfriend'),
    path(r'cancel-friend-request/<slug:link>/', cancelFriendRequest, name='cancel-friend'),
    path(r'forgot-password/', forgotPasswordView, name='forgot-password'),   
]
