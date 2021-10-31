from django.urls import path
from .views import *

app_name = 'messenger'
urlpatterns = [
    path(r'<str:link>/', chat_view, name='chat'),
    path(r'', chat_view, name='empty-chat'),
    path(r'<str:link>/send/', user_send_message_ajax, name='send'),
    path(r'<str:link>/get/', user_receiver_message_ajax, name='get-messages'),
]