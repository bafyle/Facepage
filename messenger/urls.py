from django.urls import path
from .views import chat2, getMessages, sendMessage
app_name = 'messenger'
urlpatterns = [
    path(r'<str:link>/', chat2, name='chat'),
    path(r'', chat2, name='empty-chat'),
    path(r'<str:link>/send/', sendMessage, name='send'),
    path(r'<str:link>/get/', getMessages, name='get-messages'),

]