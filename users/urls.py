from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path(r'', views.index, name='index'),
    path(r'logout/', views.logout_view, name='logout'),
    path(r'login/', views.login_with_limit_view, name='login'),
    path(r'register/', views.register_view2, name='register'),
    path(r'account-settings/', views.account_settings_view, name='account-settings'),
    path(r'delete-account/', views.delete_account_view, name='delete'),
    path(r'delete-profile-picture/', views.delete_profile_picture_view, name='delete-profile-picture'),
    path(r'delete-profile-cover/', views.delete_profile_cover_view, name='delete-profile-cover'),
    path(r'activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    path(r'personal-settings/', views.personal_settings_view, name='personal-settings'),
    path(r'send-friend-request/<slug:link>/', views.send_friend_request_view, name='add-friend'),
    path(r'accept-friend-request/<slug:link>/', views.accept_friend_request_view, name='create-friend'),
    path(r'decline-friend-request/<slug:link>/', views.decline_friend_request_view, name='decline-friend'),
    path(r'unfriend/<slug:link>/', views.unfriend_view, name='unfriend'),
    path(r'cancel-friend-request/<slug:link>/', views.cancel_friend_request_view, name='cancel-friend'),
    path(r'forgot-password/', views.forgot_password_view, name='forgot-password'),   
]
