from typing import Tuple, Union
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from users.models import Friend
from messenger.models import Message
from django.db.models import Q
import json
from .forms import SendMessageForm
from django.contrib.auth import authenticate, get_user_model as User

class ChatWebsocket(AsyncWebsocketConsumer):

    async def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.user = self.scope['user']
        await self.channel_layer.group_add(
            self.pk,
            self.channel_name
        )
        if (authentication := await self.is_user_authenticated())[0]:
            self.relation = authentication[1]
            await self.accept()
        else:
            await self.close()

    async def receive(self, text_data):
        """
        Receives data from websockets and take an action
        """
        data_in_json = json.loads(text_data)
        message_from_socket = data_in_json.get('message_input').strip()

        # validate the message using the SendMessageForm
        # from the primitive chat implementation
        # (the one with the js worker that sends ajax request every 10 second, yes xD)
        message_form = SendMessageForm(data_in_json)
        if not message_form.is_valid():
            # if message_form is invalid then send the errors dict to sender
            # of the message
            await self.send(text_data=message_form.errors.as_json())
        else:
            # if there is no error then save the message and send 
            # it back to all consumers in the channel
            message = await self.save_and_get(message=message_from_socket)
            send_date = timezone.localtime(message.send_date).strftime("%Y/%m/%d %H:%M:%S")
            sender_link = await self.get_user_link(message.sender)
            receiver_link = await self.get_user_link(message.receiver)
            await self.channel_layer.group_send(
                self.pk,
                {
                    'type': 'chat_message_correct',
                    'message': message_from_socket,
                    'send_date': send_date,
                    'sender': sender_link,
                    'receiver': receiver_link
                }
            )
    async def chat_message_correct(self, event):
        """
        send the message to the channel
        """
        await self.send(text_data=json.dumps({
            'message': event.get('message'),
            'send_date': event.get('send_date'),
            'sender': event.get("sender"),
            'receiver': event.get("receiver")
        }))
    
    async def chat_message_wrong(self, event):
        await self.send(text_data=json.dumps({
            'error': event.get('error')
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.pk,
            self.channel_name
        )
    
    @database_sync_to_async
    def is_user_authenticated(self) -> Union[Tuple, bool]:
        relation = Friend.objects.get(pk=self.pk)
        if (return_value := Friend.objects.filter(
                ((Q(side1=relation.side1) & Q(side2=relation.side2)) | (Q(side1=relation.side2) & Q(side2=relation.side1))) ).exists()):
            return return_value, relation
        else:
            return return_value
    
    @database_sync_to_async
    def save_and_get(self, message: str):
        relation = self.relation
        return Message.objects.create(message_content=message, sender=self.user, receiver=relation.side1 if relation.side2 == self.user else relation.side2)

    @database_sync_to_async
    def get_user_link(self, user: User()) -> str:
        return user.profile.link