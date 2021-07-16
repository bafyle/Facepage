from django.urls import path
from .views import chat2
app_name = 'messenger'
urlpatterns = [
    path(r'<str:link>/', chat2, name='chat'),
    path(r'', chat2, name='empty-chat'),
]