from django.urls import path
from .views import chat, send_message, chat2
app_name = 'messenger'
urlpatterns = [
    path(r'<str:username>/', chat2, name='chat'),
    path(r'', chat2, name='empty-chat'),
    #path(r'send/<str:receiver>/', send_message, name='send'),
]