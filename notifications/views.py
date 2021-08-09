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
        return render(request, 'pages/NewNotifications.html', context)
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')

def deleteNotification(request, id):
    if request.user.is_authenticated:
        notification = get_object_or_404(Notification, id=id)
        if notification.type == 'F':
            link = notification.route_id
            sender = User.objects.filter(profile__link=link).first()
            if sender:
                friendship = Friend.objects.filter((Q(side1=sender) & Q(side2=request.user)) | (Q(side1=request.user) & Q(side2=sender))).first()
                if friendship and friendship.accepted == False:
                    friendship.delete()
                else:
                    messages.error(request, "no such friend request to decline")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        notification.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')
