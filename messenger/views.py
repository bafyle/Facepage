from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from users.models import Friend
from .models import Message
from django.db.models import Q
from django.contrib.auth import get_user_model as User
from .forms import SendMessageForm
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required


@login_required
@ensure_csrf_cookie
def chat_view(request, link:str = None):
    """
    View method for rendering the template and managing all logic
    related to friends and messages
    """
    context = dict()
    friends_query = Friend.objects.filter(
        (Q(side1=request.user) | Q(side2=request.user))
    ).select_related("side1", "side2", 'side1__profile', 'side2__profile')
    context['profile_pic'] = request.user.profile.profile_picture.url
    context['navbar_name'] = request.user.first_name
    context['navbar_link'] = request.user.profile.link
    friends_list = []
    for friend in friends_query:
        if friend.side1 != request.user:
            friends_list.append(friend.side1)
        else:
            friends_list.append(friend.side2)
    context['friends'] = friends_list
    if link:
        user = User().objects.filter(profile__link=link).select_related('profile').first()
        relation = Friend.objects.filter(
            ((Q(side1=user) & Q(side2=request.user)) | (Q(side1=request.user) & Q(side2=user)))
            ).select_related("side1", "side2").first()
        if not user:
            messages.error(request, "there is no user with this link")
            return redirect('posts:home')
        if user not in friends_list:
            messages.error(request, "You can chat only with your friends")
            return redirect('posts:home')
        else:
            chat = Message.objects.select_related("sender", "receiver", 'sender__profile').filter(
                (Q(sender=request.user) & Q(receiver=user)) | 
                    (Q(sender=request.user) & Q(receiver=user)) | 
                (Q(sender=request.user) & Q(receiver=user)) | 
                (Q(sender=user) & Q(receiver=request.user))
            ).order_by('send_date')
            context['form'] = SendMessageForm()
            context['chat'] = chat
            context['his_username'] = user.profile.name()
            context['his_link'] = user.profile.link
            context['his_profile_picture_url'] = user.profile.profile_picture.url
            context['pk'] = relation.pk
            # context['active_user'] = User().objects.select_related('profile').get(pk=request.user.pk)
    return render(request, 'pages/Chat.html', context)


# These functions are used when i was sending and receiving messages through http requests
# don't use them please, use web sockets
def user_send_message_ajax(request, link: str):
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
def user_receiver_message_ajax(request, link: str):
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
