from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path(r'', index, name='index'),
    path(r'logout/', logout_view, name='logout'),
    path(r'login/', login_view, name='login'),
    path(r'register/', register_view, name='register'),
    path(r'account-settings/', accout_settings_view, name='account-settings'),
    path(r'delete-account/', delete_account_view, name='delete'),
    #path(r'changebio/', changeBioAndProfilePicture, name='change-bio'),
    path(r'delete-profile-picture/', delete_profile_picture_view, name='delete-profile-picture'),
    path(r'delete-profile-cover/', delete_profile_cover_view, name='delete-profile-cover'),
    path(r'activate/<uidb64>/<token>/', activate, name='activate'),
    path(r'personal-settings/', personal_settings_view, name='personal-settings'),
    path(r'send-friend-request/<slug:link>/', send_friend_request_view, name='add-friend'),
    path(r'accept-friend-request/<slug:link>/', accept_friend_request_view, name='create-friend'),
    path(r'decline-friend-request/<slug:link>/', decline_friend_request_view, name='decline-friend'),
    path(r'unfriend/<slug:link>/', unfriend_view, name='unfriend'),
    path(r'cancel-friend-request/<slug:link>/', cancel_friend_request_view, name='cancel-friend'),
    path(r'forgot-password/', forgot_password_view, name='forgot-password'),   
]
