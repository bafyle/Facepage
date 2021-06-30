from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from posts.models import Friend
from .models import Message
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import SendMessageForm

def chat(request, username:str = None):
    if request.user.is_authenticated:
        my_username = request.user.username
        get_friends_query = Friend.objects.filter(Q(side1__username=my_username) | 
                                                    Q(side2__username=my_username))    
        friends = []
        for friend in get_friends_query:
            if friend.side1.username == my_username:
                friends.append(friend.side2.username)
            else:
                friends.append(friend.side1.username)
        chat_information = dict()
        new_received_messages = Message.objects.filter(Q(receiver__username=my_username) & Q(seen=False))
        unseen_messages = int(new_received_messages.count())
        for m in new_received_messages:
            m.seen = True
            m.save()
        if username != None:
            chat = Message.objects.filter((Q(sender__username=my_username) & Q(receiver__username=username)) | 
                                            (Q(sender__username=username) & Q(receiver__username=my_username))).order_by('send_date')
        else:
            chat = []
        chat_information['chat'] = chat
        chat_information['my_username'] = my_username
        chat_information['his_username'] = username
        chat_information['friends'] = friends
        chat_information['unseen_messages'] = unseen_messages
        return render(request, 'messenger/chat.html', context=chat_information)
    else:
        messages.error(request, "You must login first")
        return redirect('users:index')

def send_message(request, receiver:str):
    message = request.POST['chat-input']
    receiver_user = User.objects.get(username=receiver)
    new_message = Message(sender=request.user, receiver=receiver_user, message_content = message)
    new_message.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def chat2(request, username:str = None):
    if request.user.is_authenticated:
        my_username = request.user.username
        get_friends_query = Friend.objects.filter(Q(side1__username=my_username) | 
                                                    Q(side2__username=my_username))    
        friends = []
        for friend in get_friends_query:
            if friend.side1.username == my_username:
                friends.append(friend.side2.username)
            else:
                friends.append(friend.side1.username)

        if username not in friends and username != None:
            messages.error(request, "You can chat only with your friends")
            return redirect('posts:home')
        
        chat_information = dict()
        new_received_messages = Message.objects.filter(Q(receiver__username=my_username) & Q(seen=False))
        unseen_messages = int(new_received_messages.count())
        for m in new_received_messages:
            m.seen = True
            m.save()
        if username != None:
            chat = Message.objects.filter((Q(sender__username=my_username) & Q(receiver__username=username)) | 
                                        (Q(sender__username=username) & Q(receiver__username=my_username))).order_by('send_date')
        else:
            chat = []
        chat_information['chat'] = chat
        chat_information['my_username'] = my_username
        chat_information['his_username'] = username
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
                Message.error(request, "Error in sending the message")
            chat_information['form'] = form
            return render(request, 'messenger/chat.html', context=chat_information)
        else:
            form = SendMessageForm()
            chat_information['form'] = form
            return render(request, 'messenger/chat.html', context=chat_information)
    else:
        messages.error(request, "You must login first")
        return redirect('users:index')