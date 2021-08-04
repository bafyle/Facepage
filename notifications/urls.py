from django.urls import path
from.views import testView

app_name = 'notifications'
urlpatterns = [
    path(r'', testView, name='notifications-index'),
]