from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from users.models import Friend
from .models import Message
from django.db.models import Q
from django.contrib.auth import get_user_model as User
from .forms import SendMessageForm
from django.utils import timezone


def newChat(request, link:str = None):
    if request.user.is_authenticated:
        context = dict()
        me = request.user
        friends_query = Friend.objects.filter(
            (Q(side1=me) | Q(side2=me))
            & Q(accepted=True)
        )
        context['profile_pic'] = me.profile.profile_picture.url
        context['navbar_name'] = me.first_name
        context['navbar_link'] = me.profile.link
        friends = list()
        for friend in friends_query:
            if friend.side1 != me:
                friends.append(friend.side1)
            else:
                friends.append(friend.side2)
        context['friends'] = friends
        if link:
            user = User().objects.filter(profile__link=link).first()
            if not user:
                messages.error(request, "there is no user with this link")
                return redirect('posts:home')
            if user not in friends:
                messages.error(request, "You can chat only with your friends")
                return redirect('posts:home')
            else:
                chat = Message.objects.filter(
                    (Q(sender=me) & Q(receiver=user)) | 
                    (Q(sender=user) & Q(receiver=me))
                ).order_by('send_date')
                for message in chat:
                    message.seen = True
                    message.save()
                context['form'] = SendMessageForm()
                context['chat'] = chat
                context['his_username'] = user.profile.name()
                context['his_link'] = user.profile.link
                context['his_profile_picture_url'] = user.profile.profile_picture.url
        return render(request, 'pages/Chat.html', context)



def chat(request, link:str = None):
    if request.user.is_authenticated:
        username = User().objects.filter(profile__link=link).first()
        my_username = request.user.username
        get_friends_query = Friend.objects.filter(
            (Q(side1__username=my_username) | Q(side2__username=my_username))
            & Q(accepted=True)
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
        chat_information['form'] = SendMessageForm()
        chat_information['profile_pic'] = request.user.profile.profile_picture.url
        chat_information['navbar_name'] = request.user.first_name
        chat_information['navbar_link'] = request.user.profile.link
        chat_information['username'] = request.user.username
        return render(request, 'pages/Chat.html', context=chat_information)
    else:
        messages.error(request, "You must login first")
        return redirect('users:index')


def sendMessageAjax(request, link: str):
    username = User().objects.filter(profile__link=link).first()
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message_input']
            receiver_user = User().objects.get(username=username)
            new_message = Message(sender=request.user, receiver=receiver_user, message_content = message)
            new_message.save()
            response = dict()
            response["sender"] = request.user.first_name
            response["content"] = message
            response["time"] = timezone.localtime(new_message.send_date).strftime("%Y/%m/%d %H:%M:%S")
    return JsonResponse(response)


def getMessagesAjax(request, link: str):
    my_username = request.user
    username = username = User().objects.filter(profile__link=link).first()
    chat = Message.objects.filter(
        Q(sender__username=username) & Q(receiver__username=my_username) & Q(seen=False)
    ).order_by('send_date')
    chat2 = chat.values('sender', 'message_content', 'send_date')
    response = dict()
    for index, message in enumerate(chat2):
        for key in message:
            if key == "sender":
                message[key] = User().objects.get(id=message[key]).first_name
            elif key == "send_date":
                message[key] = timezone.localtime(message[key]).strftime("%Y/%m/%d %H:%M:%S")
        response[index] = message
    for message in chat:
        message.seen = True
        message.save()
    return JsonResponse(response)
