from django.urls import path
from . import views

app_name = 'notifications'
urlpatterns = [
    path(r'', views.notifications_view, name='index'),
    path(r'delete/<slug:id>/', views.delete_notification_ajax, name='delete-notification'),
]