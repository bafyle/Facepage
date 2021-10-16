from django.urls import path
from.views import *

app_name = 'notifications'
urlpatterns = [
    path(r'', notifications_view, name='index'),
    path(r'delete/<slug:id>/', delete_notification_ajax, name='delete-notification'),
]