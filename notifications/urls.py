from django.urls import path
from.views import *

app_name = 'notifications'
urlpatterns = [
    path(r'', notificationsView, name='index'),
    path(r'delete/<slug:id>/', deleteNotificationAjax, name='delete-notification'),
]