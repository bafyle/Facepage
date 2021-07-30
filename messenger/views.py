from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from users.models import Friend
from .models import Message
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import SendMessageForm
from django.core.serializers import serialize
from django.utils import timezone

def chat(request, link:str = None):
    if request.user.is_authenticated:
        username = User.objects.filter(profile__link=link).first()
        my_username = request.user.username
        get_friends_query = Friend.objects.filter(
            Q(side1__username=my_username) | Q(side2__username=my_username)
        )    
        friends = list()
        found = False
        for friend in get_friends_query:
            if not found and (friend.side1 == username or friend.side2 == username):
                found = True 
            if friend.side1.username == my_username:
                friends.append(friend.side2)
            else:
                friends.append(friend.side1)

        if username is not None and not found:
            messages.error(request, "You can chat only with your friends")
            return redirect('posts:home')
        
        chat_information = dict()
        new_received_messages = Message.objects.filter(Q(receiver__username=my_username) & Q(seen=False))
        unseen_messages = int(new_received_messages.count())
        if username != None:
            chat = Message.objects.filter(
                (Q(sender__username=my_username) & Q(receiver__username=username)) | 
                (Q(sender__username=username) & Q(receiver__username=my_username))
            ).order_by('send_date')
        else:
            chat = []
        for message in new_received_messages:
            message.seen = True
            message.save()
        
        chat_information['chat'] = chat
        chat_information['my_name'] = request.user.profile.name()
        if username:
            chat_information['his_username'] = username.profile.name()
            chat_information['his_link'] = username.profile.link
            chat_information['his_profile_picture_url'] = username.profile.profile_picture.url
        chat_information['friends'] = friends
        chat_information['unseen_messages'] = unseen_messages
        if request.method == 'POST':
            form = SendMessageForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data['message_input']
                receiver_user = User.objects.get(username=username)
                new_message = Message(sender=request.user, receiver=receiver_user, message_content = message)
                new_message.save()
                form = SendMessageForm()
            else:
                messages.error(request, "Error in sending the message")
            chat_information['form'] = form
            chat_information['profile_pic'] = request.user.profile.profile_picture.url
            chat_information['navbar_name'] = request.user.first_name
            chat_information['navbar_link'] = request.user.profile.link
            chat_information['username'] = request.user.username
            return render(request, 'pages/Chat.html', context=chat_information)
        else:
            form = SendMessageForm()
            chat_information['form'] = form
            chat_information['profile_pic'] = request.user.profile.profile_picture.url
            chat_information['navbar_name'] = request.user.first_name
            chat_information['navbar_link'] = request.user.profile.link
            chat_information['username'] = request.user.username
            return render(request, 'pages/Chat.html', context=chat_information)
    else:
        messages.error(request, "You must login first")
        return redirect('users:index')

    

def sendMessage(request, link: str):
    username = User.objects.filter(profile__link=link).first()
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message_input']
            receiver_user = User.objects.get(username=username)
            new_message = Message(sender=request.user, receiver=receiver_user, message_content = message)
            new_message.save()
            responsef = dict()
            responsef["sender"] = request.user.first_name
            responsef["content"] = message
            responsef["time"] = timezone.localtime(new_message.send_date).strftime("%Y/%m/%d %H:%M:%S")
    return JsonResponse(responsef)


def getMessages(request, link: str):
    my_username = request.user
    username = username = User.objects.filter(profile__link=link).first()
    chat = Message.objects.filter(
        Q(sender__username=username) & Q(receiver__username=my_username) & Q(seen=False)
    ).order_by('send_date')
    chat2 = chat.values('sender', 'message_content', 'send_date')
    responsef = dict()
    for index, message in enumerate(chat2):
        for key in message:
            if key == "sender":
                message[key] = User.objects.get(id=message[key]).first_name
            elif key == "send_date":
                message[key] = timezone.localtime(message[key]).strftime("%Y/%m/%d %H:%M:%S")
        responsef[index] = message
    for message in chat:
        message.seen = True
        message.save()
    return JsonResponse(responsef)
