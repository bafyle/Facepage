from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponseRedirect

from .models import Notification
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
        notification.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "you need to login first")
        return redirect('users:index')
