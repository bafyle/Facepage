import json
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Notification
from users.models import Friend
# Create your views here.

def notificationsView(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user_to=request.user).order_by('-date')[0:10]
        context = {
            'navbar_name': request.user.first_name,
            'navbar_link': request.user.profile.link,
            'profile_pic': request.user.profile.profile_picture.url,
            'notifications': notifications,
        }
        notifications.update(seen=True)
        return render(request, 'pages/NewNotifications.html', context)
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')

def deleteNotificationAjax(request, id):
    if request.user.is_authenticated:
        notification = Notification.objects.filter(id=id).first()
        if notification:
            if notification.type == 'F':
                link = notification.route_id
                sender = User.objects.filter(profile__link=link).first()
                if sender:
                    friendship = Friend.objects.filter((Q(side1=sender) & Q(side2=request.user)) | (Q(side1=request.user) & Q(side2=sender))).first()
                    if friendship and friendship.accepted == False:
                        friendship.delete()
                    else:
                        messages.error(request, "no such friend request to decline")
                        return JsonResponse({"message":"no-friend"})
            notification.delete()
            return JsonResponse({"message":"good"})
        else:
            return JsonResponse({"message":"no-notification"})
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')
