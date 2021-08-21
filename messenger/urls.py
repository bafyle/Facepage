from django.urls import path
from .views import *

app_name = 'messenger'
urlpatterns = [
    path(r'<str:link>/', newChat, name='chat'),
    path(r'', newChat, name='empty-chat'),
    path(r'<str:link>/send/', sendMessageAjax, name='send'),
    path(r'<str:link>/get/', getMessagesAjax, name='get-messages'),
]