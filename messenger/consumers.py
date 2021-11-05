from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync, sync_to_async
from django.utils import timezone
from users.models import Friend
from messenger.models import Message
from django.db.models import Q
import json
from django.core.exceptions import ValidationError

class ChatWebsocket(AsyncWebsocketConsumer):

    async def connect(self):
        """
        Decides if the incoming connection is 
        authorized or not to join this group
        """
        self.user = self.scope['user']
        self.pk = self.scope['url_route']['kwargs']['pk']

        await self.channel_layer.group_add(
            self.pk,
            self.channel_name
        )
        if await self.is_user_authenticated():
            await self.accept()
        else:
            await self.close()

    async def receive(self, text_data):
        """
        Receives data from websockets and take an action
        """
        data_in_json = json.loads(text_data)
        message_from_socket = data_in_json.get('message_input').strip()
        
        # if there is an error, send the error to the user who sent
        # the invalid data
        try:
            message = await self.save_and_get(message=message_from_socket)
        except ValidationError as error:
            await self.send(text_data=json.dumps({
                'error': error.messages
            }))
        else:
            # if there is no error, send the message to all people in the channel
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
    def is_user_authenticated(self):
        relation = Friend.objects.get(pk=self.pk)
        return Friend.objects.filter(
                ((Q(side1=relation.side1) & Q(side2=relation.side2)) | (Q(side1=relation.side2) & Q(side2=relation.side1))) &  
                Q(accepted=True)).exists()
    
    @database_sync_to_async
    def save_and_get(self, message):
        relation = Friend.objects.get(pk=self.pk)
        return Message.objects.create(message_content=message, sender=self.user, receiver=relation.side1 if relation.side2 == self.user else relation.side2)
    
    @database_sync_to_async
    def get_user_link(self, user):
        return user.profile.link